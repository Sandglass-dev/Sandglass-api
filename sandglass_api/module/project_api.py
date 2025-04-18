from flask import Blueprint, request
from flask_jwt_extended import jwt_required, current_user
from mongoengine import QuerySet, FieldDoesNotExist, ValidationError

from sandglass_api.models.project import Project

project_api = Blueprint('project_api', __name__)


def abstract_get_proj_by_id(proj_id: str):
    try:
        p: Project = Project.objects().with_id(proj_id)
        if not p:
            return b'', 404
    except ValidationError as e:
        return str(e), 400
    return p, 200


@project_api.get('/proj')
@jwt_required()
def get_proj_by_current_user():
    """
    Get projects owned by the current user.

    STATUS CODES:
    200 - Success.
    """
    select_related: bool = request.args.get('select_related', False, bool)
    proj: QuerySet = Project.objects(owner=current_user)
    return proj.to_json() if select_related else proj.only('id').to_json()

@project_api.get('/proj/<string:proj_id>')
@jwt_required()
def get_proj_by_id(proj_id: str):
    """
    Get the project with given id.

    STATUS CODES:
    200 - Success.
    400 - Invalid id format.
    404 - Project with given id not found.
    """
    result, code = abstract_get_proj_by_id(proj_id)
    return result.to_json() if code == 200 else (result, code)

@project_api.post('/proj')
@jwt_required()
def create_proj():
    """
    Create a new project.
    Return the id of the created project.

    STATUS CODES:
    201 - Project created.
    400 - An invalid field was passed.
    """
    try:
        p = Project(owner=current_user, **request.json).save(cascade=True)
    except FieldDoesNotExist as e:
        return str(e), 400
    return str(p.id), 201

@project_api.delete('/proj/<string:proj_id>')
@jwt_required()
def delete_proj(proj_id: str):
    """
    Delete project with given id.

    STATUS CODES:
    204 - Project deleted.
    400 - Invalid id format.
    404 - Project with given id not found.
    """
    result, code = abstract_get_proj_by_id(proj_id)
    if code != 200:
        return result, code
    result.delete()
    return b'', 204
