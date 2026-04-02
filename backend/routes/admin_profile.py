from flask import Blueprint, request, jsonify
from db import DatabaseConnection
from psycopg2.extras import RealDictCursor
from utils.auth_utils import require_auth

admin_profile_bp = Blueprint('admin_profile', __name__)

@admin_profile_bp.route('/get', methods=['GET'])
@require_auth(['admin'])
def get_admin_profile(current_user):
    """Fetch current admin's profile details."""
    try:
        with DatabaseConnection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, full_name, email, role, organization_name 
                    FROM users WHERE id = %s AND role = 'admin'
                """, (current_user['sub'],))
                user_data = cur.fetchone()
                
                if not user_data:
                    return jsonify({"error": "Admin not found"}), 404
                
                # Admin profile fetch (orgName is plaintext now)
                
                return jsonify({"user": user_data, "accessLevel": "SUPER_USER"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_profile_bp.route('/update', methods=['POST'])
@require_auth(['admin'])
def update_admin_profile(current_user):
    """Update admin profile fields."""
    data = request.json
    full_name = data.get('full_name')
    org_name = data.get('organization_name')
    
    try:
        with DatabaseConnection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE users 
                    SET full_name = %s, organization_name = %s 
                    WHERE id = %s AND role = 'admin'
                """, (full_name, org_name, current_user['sub']))
                conn.commit()
                return jsonify({"message": "Admin profile updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

