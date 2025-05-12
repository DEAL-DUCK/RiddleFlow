from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Result
from sqlalchemy.orm import load_only, selectinload, joinedload

from core.models import (
    Hackathon,
    Jury,
    JuryHackathonAssociation,
    JuryEvaluation,
    HackathonSubmission,
    HackathonTask,
    User, HackathonUserAssociation
)
from core.models.hackathon import HackathonStatus
from .schemas import JuryResponse, JuryCreate
from fastapi import HTTPException, status

from ..evaluations.schemas import EvaluationReadSchema


def any_not(ann: str):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'{ann} not found.')

async def add_jury_to_hackathon(
        session: AsyncSession,
        user : User,
        hackathon : Hackathon
):
    user_check = await session.scalar(
        select(HackathonUserAssociation)
        .where(Hackathon.id == hackathon.id)
        .where(User.id == user.id
    )
    .where(User.id == user.id))
    if user_check:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь уже участвует в этом хакатоне"
        )
    jury_association = await session.scalar(
        select(JuryHackathonAssociation)
        .join(Jury, JuryHackathonAssociation.jury_id == Jury.id)
        .where(Jury.user_id == user.id)
        .where(JuryHackathonAssociation.hackathon_id == hackathon.id)
    )

    if jury_association:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь уже судит в этом хакатоне"
        )

    jury = await session.scalar(
        select(Jury).where(Jury.user_id == user.id)
    )

    if not jury:
        jury = Jury(user_id=user.id)
        session.add(jury)
        await session.flush()
    new_association = JuryHackathonAssociation(
        jury_id=jury.id,
        hackathon_id=hackathon.id
    )
    session.add(new_association)
    await session.commit()

    return {
        "status": "success",
        "message": "Пользователь добавлен в жюри хакатона",
        "jury_id": jury.id,
        "hackathon_id": hackathon.id
    }




async def remove_jury_from_hackathon(
        session: AsyncSession,
        jury:Jury,
        hackathon:Hackathon,
):
    if hackathon.status == HackathonStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail='нельзя удалить жюри из активного хакатона')
    jury_association = await session.scalar(
        select(JuryHackathonAssociation)
        .join(Jury, JuryHackathonAssociation.jury_id == Jury.id)
        .where(Jury.id == jury.id)
        .where(JuryHackathonAssociation.hackathon_id == hackathon.id)
    )
    await session.delete(jury_association)
    await session.delete(jury)
    await session.commit()
    return {'ok':f'jury {jury.id} deleted from hackathon {hackathon.id}'}

async def get_hackathons_judged_by_jury(session: AsyncSession,jury:Jury):
    result = await session.execute(
        select(Hackathon)
        .join(JuryHackathonAssociation, Hackathon.id == JuryHackathonAssociation.hackathon_id)
        .where(JuryHackathonAssociation.jury_id == jury.id)
        .options(
            load_only(
                Hackathon.id,
                Hackathon.title,
                Hackathon.description,
                Hackathon.status,
                Hackathon.start_time,
                Hackathon.end_time,
            ),
        )
    )

    hackathons = result.scalars().all()
    return [
        {
            "id": hackathon.id,
            "title": hackathon.title,
            "description": hackathon.description,
            "status": hackathon.status.value,
            "start_time": hackathon.start_time.isoformat() if hackathon.start_time else None,
            "end_time": hackathon.end_time.isoformat() if hackathon.end_time else None,
            "logo_url": hackathon.logo_url,
        }
        for hackathon in hackathons
    ]

async def get_jury_evaluations_with_details(
    session: AsyncSession,
    jury:Jury
):
        query = (
            select(
                HackathonSubmission.description,
                JuryEvaluation.score,
                JuryEvaluation.comment,
                HackathonSubmission.id.label("submission_id"),
                HackathonTask.title.label("task_title"),
                Hackathon.title.label("hackathon_title")
            )
            .select_from(JuryEvaluation)
            .join(HackathonSubmission, JuryEvaluation.submission_id == HackathonSubmission.id)
            .join(HackathonTask, HackathonTask.id == HackathonSubmission.task_id)
            .join(Hackathon, Hackathon.id == HackathonTask.hackathon_id)
            .where(JuryEvaluation.jury_id == jury.id)
        )

        result = await session.execute(query)
        evaluations = result.all()
        return {
            row.description: {
                "score": float(row.score),
                "comment": row.comment,
                "submission_id": row.submission_id,
                "task": row.task_title,
                "hackathon": row.hackathon_title
            }
            for row in evaluations
        }


async def get_jury_evaluations_with_this_hackathon(
        session: AsyncSession,
        jury: Jury,
        hackathon : Hackathon
):
    stmt = (
        select(JuryEvaluation)
        .where(
            JuryEvaluation.hackathon_id == hackathon.id,
            JuryEvaluation.jury_id == jury.id
        )
        .options(
            joinedload(JuryEvaluation.jury),
            joinedload(JuryEvaluation.submission),
            joinedload(JuryEvaluation.hackathon)
        )
        .order_by(JuryEvaluation.created_at.desc())
    )

    result = await session.execute(stmt)
    evaluations = result.scalars().all()
    return [EvaluationReadSchema.model_validate(eval) for eval in evaluations]
async def get_all_my_evaluation(
        session : AsyncSession,
        jury : Jury
):
    stmt = select(JuryEvaluation).where(JuryEvaluation.jury == jury)
    result:Result  = await session.execute(stmt)
    evaluation = result.scalars().all()
    return [EvaluationReadSchema.model_validate(eval) for eval in evaluation]
