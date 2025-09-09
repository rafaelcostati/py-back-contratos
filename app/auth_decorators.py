# app/auth_decorators.py
from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get("perfil") != "Administrador":
                return jsonify({"error": "Acesso restrito a administradores"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def fiscal_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get("perfil") not in ["Fiscal", "Administrador"]:
                return jsonify({"error": "Acesso restrito a fiscais e administradores"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

