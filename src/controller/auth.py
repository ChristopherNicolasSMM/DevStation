"""
Controlador de autenticação.
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from model.user import User
from db.database import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Endpoint para login do usuário."""
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('web.dashboard'))
        return render_template('auth/login.html')
    
    data = request.get_json() if request.is_json else request.form
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        if request.is_json:
            return jsonify({'error': 'Username e password são obrigatórios'}), 400
        flash('Username e password são obrigatórios', 'error')
        return render_template('auth/login.html')
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        if user.is_active:
            login_user(user)
            if request.is_json:
                return jsonify({
                    'message': 'Login realizado com sucesso',
                    'user': user.to_dict()
                }), 200
            flash('Login realizado com sucesso', 'success')
            return redirect(url_for('web.dashboard'))
        else:
            if request.is_json:
                return jsonify({'error': 'Usuário inativo'}), 401
            flash('Usuário inativo', 'error')
            return render_template('auth/login.html')
    else:
        if request.is_json:
            return jsonify({'error': 'Credenciais inválidas'}), 401
        flash('Credenciais inválidas', 'error')
        return render_template('auth/login.html')

@auth_bp.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    """Endpoint para logout do usuário."""
    logout_user()
    if request.is_json:
        return jsonify({'message': 'Logout realizado com sucesso'}), 200
    flash('Logout realizado com sucesso', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['POST'])
def register():
    """Endpoint para registro de novo usuário."""
    data = request.get_json() if request.is_json else request.form
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        if request.is_json:
            return jsonify({'error': 'Username, email e password são obrigatórios'}), 400
        flash('Username, email e password são obrigatórios', 'error')
        return redirect(url_for('auth.login'))
    
    # Verificar se usuário já existe
    if User.query.filter_by(username=username).first():
        if request.is_json:
            return jsonify({'error': 'Username já existe'}), 400
        flash('Username já existe', 'error')
        return redirect(url_for('auth.login'))
    
    if User.query.filter_by(email=email).first():
        if request.is_json:
            return jsonify({'error': 'Email já existe'}), 400
        flash('Email já existe', 'error')
        return redirect(url_for('auth.login'))
    
    # Criar novo usuário
    user = User(
        username=username,
        email=email
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    if request.is_json:
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user': user.to_dict()
        }), 201
    
    flash('Usuário criado com sucesso', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """Endpoint para obter perfil do usuário logado."""
    if request.is_json:
        return jsonify({'user': current_user.to_dict()}), 200
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Endpoint para alterar senha do usuário."""
    data = request.get_json() if request.is_json else request.form
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        if request.is_json:
            return jsonify({'error': 'Senha atual e nova senha são obrigatórias'}), 400
        flash('Senha atual e nova senha são obrigatórias', 'error')
        return redirect(url_for('auth.profile'))
    
    if not current_user.check_password(current_password):
        if request.is_json:
            return jsonify({'error': 'Senha atual incorreta'}), 401
        flash('Senha atual incorreta', 'error')
        return redirect(url_for('auth.profile'))
    
    current_user.set_password(new_password)
    db.session.commit()
    
    if request.is_json:
        return jsonify({'message': 'Senha alterada com sucesso'}), 200
    
    flash('Senha alterada com sucesso', 'success')
    return redirect(url_for('auth.profile'))
