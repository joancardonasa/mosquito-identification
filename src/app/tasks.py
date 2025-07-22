import logging
from celery import Celery
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Observation, IdentificationTask
from app.ai_classifier import AIClassifier

logger = logging.getLogger(__name__)

celery = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

@celery.task
def classify_observation_ai(observation_id: int):
    db: Session = SessionLocal()
    try:
        obs = db.get(Observation, observation_id)
        if obs:
            classifier = AIClassifier()
            classification = classifier.classify(obs.photo_path)
            if not classification:
                logger.info(f"Observation {observation_id} could not be classified, skipping update")
                return

            id_task = db.query(IdentificationTask).filter_by(observation_id=observation_id).first()
            
            if id_task is None:
                id_task = IdentificationTask(
                    observation_id=observation_id,
                    ai_classification=classification
                )
                db.add(id_task)
            else:
                id_task.ai_classification = classification
            
            db.commit()
            db.refresh(id_task)

            logger.info(f"Observation {observation_id} classified as {classification}")
        else:
            logger.warning(f"Observation {observation_id} not found")
    except Exception as e:
        logger.error(f"Error classifying observation {observation_id}: {e}")
        raise
    finally:
        db.close()
