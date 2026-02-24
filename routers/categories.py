from flask import Blueprint, jsonify, request
from sqlalchemy import select
from pydantic import ValidationError

from core.db import db
from models.categories import Category
from schemas.questions import ( CategoryResponse, CategoryUpdate,
    QuestionList,
    QuestionRetrieve,
    QuestionCreateRequest,
    QuestionCreateResponse,
    QuestionUpdateRequest,
    CategoryBase
)


category_bp = Blueprint(
    "categories",
    __name__,  # questions.py
    url_prefix="/categories"
)

@category_bp.route("", methods=["GET"])
def get_all_categories():
    stmt = select(Category)
    result = db.session.execute(stmt).scalars().all()

    response = [
        CategoryResponse.model_validate(obj).model_dump()
        for obj in result
    ]

    return jsonify(response), 200


@category_bp.route("", methods=["POST"])
def create_category():
    raw_data = request.get_json(silent=True)

    if not raw_data:
        return jsonify({"error": "Request body is missing or invalid JSON"}), 400

    try:
        validated = CategoryBase.model_validate(raw_data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    try:
        category = Category(**validated.model_dump())
        db.session.add(category)
        db.session.commit()
        db.session.refresh(category)
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Failed to create category",
            "detail": str(e)
        }), 500

    return jsonify(
        CategoryResponse.model_validate(category).model_dump()
    ), 201


@category_bp.route("/<int:category_id>", methods=["PUT"])
def update_category(category_id: int):
    raw_data = request.get_json(silent=True)

    if not raw_data:
        return jsonify({"error": "Request body is missing or invalid JSON"}), 400

    try:
        validated = CategoryUpdate.model_validate(raw_data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    category = db.session.get(Category, category_id)

    if not category:
        return jsonify({"error": "Category not found"}), 404

    try:
        for key, value in validated.model_dump(exclude_none=True).items():
            setattr(category, key, value)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Failed to update category",
            "detail": str(e)
        }), 500

    return jsonify(
        CategoryResponse.model_validate(category).model_dump()
    ), 200


@category_bp.route("/<int:category_id>", methods=["DELETE"])
def delete_category(category_id: int):
    category = db.session.get(Category, category_id)

    if not category:
        return jsonify({"error": "Category not found"}), 404

    try:
        db.session.delete(category)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Failed to delete category",
            "detail": str(e)
        }), 500

    return "", 204
