# data/prepare_data.py
# обработка датасета PeerRead 

from collections import defaultdict
from pathlib import Path
import json
import os

from scientific_review.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

SAVE_PATH = "data/processed/peerread.json"
MAX_SAMPLES = None          # None = все
MAX_TEXT_LENGTH = None      


def get_paper_id_from_parsed(paper_json: dict, filename: str) -> str:
    """
    Извлекаем ID из parsed pdf
    
    Args:
        paper_json: словарь с metadata
        filename: имя файла
    
    Returns: 
        ID статьи
    """
    if isinstance(paper_json, dict):
        meta = paper_json.get("metadata") or paper_json
        if meta.get("id"):
            return str(meta["id"]).strip()
        if meta.get("name"):
            return Path(meta["name"]).stem.replace(".pdf", "")
    return Path(filename).stem.replace(".pdf", "")


def extract_scores(review_obj: dict) -> dict | None:
    """
    Извлекаем 4 нужных аспекта. 
    Теперь более устойчиво к ICLR-структуре (IS_ANNOTATED, IMPACT, SOUNDNESS и т.д.)
    
    Args:
        review_obj: словарь с оценками
    
    Returns:    
        Словарь с оценками или None, если совсем нет данных
    """
    try:
        if not isinstance(review_obj, dict):
            return None

        # пропускаем неаннотированные ревью (мета-ревью, вопросы и т.д.)
        if review_obj.get("IS_ANNOTATED") is False:
            return None

        scores = {
            "originality": float(review_obj.get("ORIGINALITY", review_obj.get("originality", -1))),
            "soundness":   float(review_obj.get("SOUNDNESS_CORRECTNESS",
                               review_obj.get("soundness_correctness",
                               review_obj.get("soundness", -1)))),
            "clarity":     float(review_obj.get("CLARITY", review_obj.get("clarity", -1))),
            "substance":   float(review_obj.get("SUBSTANCE", review_obj.get("substance", -1))),
        }

        # если все аспекты отсутствуют — отбрасываем ревью
        if any(v < 0 for v in scores.values()):
            return None

        return scores

    except (ValueError, TypeError):
        return None


def build_text(paper_json: dict) -> str:
    """
    Собираем текст из sections
    
    Args:
        paper_json: словарь с metadata
    
    Returns:
        Текст статьи
    """
    try:
        meta = paper_json.get("metadata") or paper_json
        sections = meta.get("sections", [])
        texts = []
        for s in sections:
            if isinstance(s, dict):
                texts.append(s.get("text", ""))
            elif isinstance(s, str):
                texts.append(s)
        full = "\n\n".join(texts).strip()
        if MAX_TEXT_LENGTH:
            return full[:MAX_TEXT_LENGTH]
        return full
    except:
        return ""


def load_data():
    """
    Загружаем данные из PeerRead (включая все группы)
    
    Returns:
        Словарь с статьями и список ревью
    """
    base = Path("data/raw/raw_peerread")
    papers_dict = {}          
    reviews_dict = defaultdict(list)

    conferences = [
        "iclr_2017",
        "acl_2017",
        "arxiv.cs.ai_2007-2017",
        "arxiv.cs.cl_2007-2017",
        "arxiv.cs.lg_2007-2017",
        "conll_2016",
        "nips_2013-2017",
    ]

    for conf in conferences:
        conf_path = base / conf
        if not conf_path.exists():
            logger.warning(f"Папка не найдена: {conf_path}")
            continue

        logger.info(f"Обрабатываем группу: {conf}")

        # parsed_pdfs
        for split in ["train", "dev", "test"]:
            pdir = conf_path / split / "parsed_pdfs"
            if not pdir.exists():
                pdir = conf_path / "parsed_pdfs"
            if not pdir.exists():
                continue

            for f in pdir.glob("*.json"):
                try:
                    with open(f, encoding="utf-8") as fp:
                        data = json.load(fp)
                    pid = get_paper_id_from_parsed(data, f.name)
                    if pid:
                        papers_dict[pid] = data
                except Exception as e:
                    logger.warning(f"Ошибка статьи {f.name}: {e}")

        # reviews
        for split in ["train", "dev", "test"]:
            rdir = conf_path / split / "reviews"
            if not rdir.exists():
                rdir = conf_path / "reviews"
            if not rdir.exists():
                continue

            for f in rdir.glob("*.json"):
                try:
                    with open(f, encoding="utf-8") as fp:
                        data = json.load(fp)
                    pid = str(data.get("id") or Path(f.name).stem).strip()

                    revs = data.get("reviews", [])
                    if not isinstance(revs, list):
                        revs = [data]

                    reviews_dict[pid].extend(revs)
                except Exception as e:
                    logger.warning(f"Ошибка ревью {f.name}: {e}")

    logger.info(f"Загружено статей: {len(papers_dict)} | Групп ревью: {len(reviews_dict)}")
    return papers_dict, reviews_dict


def prepare_dataset():
    """
    Собираем данные из PeerRead
    
    Returns:
        Список словарей с текстом статьи и оценками        
    """
    papers_dict, reviews_dict = load_data()
    final_data = []

    logger.info("Сопоставляем и фильтруем...")

    for pid, paper_json in papers_dict.items():
        if pid not in reviews_dict:
            continue

        text = build_text(paper_json)
        if len(text) < 300:
            continue

        # ЖЕСТКОЕ ОТБРАСЫВАНИЕ ДЛИННЫХ СТАТЕЙ
        if len(text) > 40000:
           continue   # выкидываем всё, что длиннее 40k

        scores_list = []
        for rev in reviews_dict[pid]:
            if isinstance(rev, dict) and "reviews" in rev and isinstance(rev["reviews"], list):
                for inner in rev["reviews"]:
                    sc = extract_scores(inner)
                    if sc:
                        scores_list.append(sc)
            else:
                sc = extract_scores(rev)
                if sc:
                    scores_list.append(sc)

        # если после фильтрации не осталось ни одного валидного ревью - пропускаем статью
        if not scores_list:
            continue

        # усредняем
        avg_scores = {
            "novelty":       sum(s["originality"] for s in scores_list) / len(scores_list),
            "scientificity": sum(s["soundness"]   for s in scores_list) / len(scores_list),
            "readability":   sum(s["clarity"]     for s in scores_list) / len(scores_list),
            "complexity":    sum(s["substance"]   for s in scores_list) / len(scores_list),
        }
        final_score = sum(avg_scores.values()) / 4
        avg_scores["final_score"] = round(final_score, 3)

        # приводим к шкале 0-10
        #avg_scores = {k: round(v * 2, 3) for k, v in avg_scores.items()}

        final_data.append({
            "id": pid,
            "text": text,
            "scores": avg_scores,
            "num_reviews": len(scores_list)
        })

        if MAX_SAMPLES and len(final_data) >= MAX_SAMPLES:
            break

    logger.info(f"Собрано статей с валидными оценками: {len(final_data)}")

    # статистика длин текстов
    if final_data:
        lengths = [len(item["text"]) for item in final_data]
        avg_len = sum(lengths) / len(lengths)
        max_len = max(lengths)
        
        logger.info(f"Статистика длин текстов:")
        logger.info(f"  Всего статей: {len(final_data)}")
        logger.info(f"  Средняя длина: {avg_len:.0f} символов")
        logger.info(f"  Максимальная длина: {max_len} символов")
        
        # показать статистику длин текстов по размерам статей
        for threshold in [5000, 10000, 15000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000]:
            count = sum(1 for l in lengths if l > threshold)
            logger.info(f"  > {threshold:5d} символов: {count} статей")

    return final_data


def main():
    """
    Собираем данные из PeerRead и сохраняем в json
    """
    data = prepare_dataset()
    if not data:
        logger.error("Не удалось собрать ни одной статьи!")
        return

    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"Сохранено: {SAVE_PATH} ({len(data)} записей)")


if __name__ == "__main__":
    main()
