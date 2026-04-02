from flask import Blueprint, request, jsonify
from utils.auth_utils import require_auth
from db import DatabaseConnection
from psycopg2.extras import RealDictCursor
from utils.crypto_utils import decrypt_data

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/organizers/pending', methods=['GET'])
@require_auth(roles=['admin'])
def get_pending_organizers(current_user):
    """
    Get a list of all organizers that are currently in 'pending' status for THIS admin's club.
    """
    try:
        club_id = current_user.get('club_id')
        if not club_id:
             return jsonify([]), 200 # Should not happen for admin but safety first

        with DatabaseConnection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, full_name, email, reg_no, phone_number, organization_name, dob, address, created_at
                    FROM users 
                    WHERE role = 'organizer' 
                    AND account_status = 'pending'
                    AND club_id = %s 
                    ORDER BY created_at DESC
                """, (club_id,))
                organizers = cur.fetchall()
                
                # Decrypt only personal fields (orgName is plaintext now)
                result = []
                for row in organizers:
                    org = dict(row)
                    org['phone_number'] = decrypt_data(org['phone_number'])
                    org['dob'] = decrypt_data(org['dob'])
                    org['address'] = decrypt_data(org['address'])
                    result.append(org)
                    
                return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@admin_bp.route('/organizers/active', methods=['GET'])
@require_auth(roles=['admin'])
def get_active_organizers(current_user):
    """
    Get a list of all organizers that are currently approved ('active') for THIS admin's club.
    """
    try:
        club_id = current_user.get('club_id')
        if not club_id:
             return jsonify([]), 200

        with DatabaseConnection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, full_name, email, reg_no, phone_number, organization_name, created_at
                    FROM users 
                    WHERE role = 'organizer' 
                    AND account_status = 'active'
                    AND club_id = %s 
                    ORDER BY full_name ASC
                """, (club_id,))
                organizers = cur.fetchall()
                
                result = []
                for row in organizers:
                    org = dict(row)
                    org['phone_number'] = decrypt_data(org['phone_number'])
                    result.append(org)
                    
                return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/organizers/<int:user_id>/<action>', methods=['POST'])
@require_auth(roles=['admin'])
def process_organizer(current_user, user_id, action):
    """
    Approve or reject an organizer account.
    Works for both new applicants and existing members (revocation).
    """
    if action not in ['approve', 'reject']:
        return jsonify({"error": "Invalid action parameter"}), 400
        
    new_status = 'active' if action == 'approve' else 'rejected'
    club_id = current_user.get('club_id')
    if not club_id:
        return jsonify({"error": "Admin has no assigned club."}), 403
    
    try:
        with DatabaseConnection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    UPDATE users 
                    SET account_status = %s 
                    WHERE id = %s 
                    AND role = 'organizer' 
                    AND club_id = %s 
                    RETURNING id, email, full_name, organization_name
                """, (new_status, user_id, club_id))
                
                updated = cur.fetchone()
                
                if not updated:
                    return jsonify({"error": "Organizer not found or belongs to another organization"}), 404
                
                # Send Notification Email
                from utils.email_utils import send_organizer_status_email
                send_organizer_status_email(updated['email'], updated['full_name'], new_status, updated['organization_name'])
                    
                conn.commit()
                return jsonify({"message": f"Organizer successfully {new_status}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- EVENT MANAGEMENT FOR ADMINS ---

@admin_bp.route('/events/pending', methods=['GET'])
@require_auth(roles=['admin'])
def get_pending_events(current_user):
    """Fetch all pending event requests for the admin's organization."""
    try:
        club_id = current_user.get('club_id')
        if not club_id:
            return jsonify([]), 200

        with DatabaseConnection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT e.*, h.name as hall_name, u.full_name as organizer_name, u.organization_name as club_name
                    FROM events e 
                    LEFT JOIN halls h ON e.hall_id = h.id
                    LEFT JOIN users u ON e.organizer_id = u.id
                    WHERE e.status = 'pending'
                    AND e.club_id = %s 
                    ORDER BY e.created_at ASC
                """, (club_id,))
                
                events = cur.fetchall()
                
                # Check Hall Availability for each event
                for event in events:
                    # Check if ANY approved event is already in this hall for these exact dates (overlap check)
                    cur.execute("""
                        SELECT id FROM events 
                        WHERE hall_id = %s 
                        AND status = 'approved'
                        AND id != %s
                        AND (
                            (start_date <= %s AND end_date >= %s) OR
                            (start_date <= %s AND end_date >= %s) OR
                            (start_date >= %s AND end_date <= %s)
                        )
                    """, (
                        event['hall_id'], event['id'], 
                        event['start_date'], event['start_date'],
                        event['end_date'], event['end_date'],
                        event['start_date'], event['end_date']
                    ))
                    conflict = cur.fetchone()
                    event['hall_available'] = (conflict is None)
                    
                    # If occupied, suggest other halls free for THESE dates
                    event['alternative_halls'] = []
                    if conflict:
                        cur.execute("""
                            SELECT name FROM halls 
                            WHERE id NOT IN (
                                SELECT hall_id FROM events 
                                WHERE status = 'approved'
                                AND (
                                    (start_date <= %s AND end_date >= %s) OR
                                    (start_date <= %s AND end_date >= %s) OR
                                    (start_date >= %s AND end_date <= %s)
                                )
                            )
                        """, (
                            event['start_date'], event['start_date'],
                            event['end_date'], event['end_date'],
                            event['start_date'], event['end_date']
                        ))
                        alts = cur.fetchall()
                        event['alternative_halls'] = [a['name'] for a in alts]
                    
                return jsonify(events), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/events/approved', methods=['GET'])
@require_auth(roles=['admin'])
def get_approved_events_for_admin(current_user):
    """Fetch all approved event requests for the admin's organization."""
    try:
        club_id = current_user.get('club_id')
        if not club_id:
            return jsonify([]), 200

        with DatabaseConnection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT e.*, h.name as hall_name, u.full_name as organizer_name, 
                           u.organization_name as club_name, a.full_name as approved_by_name
                    FROM events e 
                    LEFT JOIN halls h ON e.hall_id = h.id
                    LEFT JOIN users u ON e.organizer_id = u.id
                    LEFT JOIN users a ON e.approved_by = a.id
                    WHERE e.status = 'approved'
                    AND e.club_id = %s 
                    ORDER BY e.start_date ASC
                """, (club_id,))
                
                events = cur.fetchall()
                # ISO format dates for JS
                for e in events:
                    if e['start_date']: e['start_date'] = e['start_date'].isoformat()
                    if e['end_date']: e['end_date'] = e['end_date'].isoformat()
                    if e['reg_deadline']: e['reg_deadline'] = e['reg_deadline'].isoformat()
                    if e['created_at']: e['created_at'] = e['created_at'].isoformat()
                    
                return jsonify(events), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/clubs', methods=['GET'])
@require_auth(roles=['admin'])
def get_admin_clubs(current_user):
    """Fetch the list of clubs this admin is responsible for."""
    try:
        club_name = current_user.get('orgName', '')
        clubs = [c.strip() for c in club_name.split(',') if c.strip()]
        return jsonify(clubs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/events/<int:event_id>/process', methods=['POST'])
@require_auth(roles=['admin'])
def process_event(current_user, event_id):
    """Approve or reject an event with a message."""
    data = request.json
    action = data.get('action') # 'approve' or 'reject'
    message = data.get('message', "")
    
    if action not in ['approved', 'rejected']:
        return jsonify({"error": "Invalid action"}), 400
        
    try:
        with DatabaseConnection() as conn:
            with conn.cursor() as cur:
                # Security: Ensure this event belongs to the specific club ID this admin manages
                club_id = current_user.get('club_id')
                if not club_id:
                    return jsonify({"error": "Admin has no assigned club."}), 403
                
                cur.execute("""
                    SELECT id FROM events 
                    WHERE id = %s AND club_id = %s
                """, (event_id, club_id))
                
                if not cur.fetchone():
                    return jsonify({"error": "Unauthorized to process events for this organization"}), 403

                cur.execute("""
                    UPDATE events 
                    SET status = %s, admin_message = %s, approved_by = %s 
                    WHERE id = %s
                """, (action, message, current_user['sub'], event_id))
                conn.commit()
                return jsonify({"message": f"Event has been {action}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
