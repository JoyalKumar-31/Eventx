"""
tools/profile_tools.py - User & Student Profile Management Tools
Enables Fest AI Copilot to inspect and update student profiles in real-time.
"""

import re
from typing import Dict, Any, Optional, List, Tuple


def normalize_year_of_study(raw_val: str) -> Optional[str]:
    """
    Normalizes various year representations into standard database string values:
    '1st Year', '2nd Year', '3rd Year', '4th Year', 'Postgraduate / PhD'
    """
    if not raw_val:
        return None
    val = raw_val.lower().strip()
    
    # 1st Year matches
    if any(k in val for k in ["1st", "first", "1 year", "1 yr", "year 1"]) or val == "1":
        return "1st Year"
    # 2nd Year matches
    elif any(k in val for k in ["2nd", "second", "2 year", "2 yr", "year 2"]) or val == "2":
        return "2nd Year"
    # 3rd Year matches
    elif any(k in val for k in ["3rd", "third", "3 year", "3 yr", "year 3"]) or val == "3":
        return "3rd Year"
    # 4th Year matches
    elif any(k in val for k in ["4th", "fourth", "4 year", "4 yr", "year 4", "final year"]) or val == "4":
        return "4th Year"
    # Postgraduate matches
    elif any(k in val for k in ["postgraduate", "pg", "phd", "master", "5th"]):
        return "Postgraduate / PhD"
    
    # If already formatted or other
    if "year" in val:
        return val.title()
    return f"{raw_val.strip()} Year"


def parse_profile_update_intent(text: str) -> Dict[str, Any]:
    """
    Parses natural language requests to change profile fields.
    Returns a dict with detected update fields:
    {
       'year_of_study': '3rd Year',
       'department': '...',
       'phone': '...',
       'college_name': '...',
       'student_id_number': '...',
       'full_name': '...'
    }
    """
    lower = text.lower().strip()
    updates: Dict[str, Any] = {}

    # 1. Year of study:
    # "from 1st year to 3rd year", "change my year to 3rd year", "year to 3rd", "set year = 2nd year"
    year_target = None
    # Pattern: "to <target year>" e.g. "from 1st year to 3rd year", "to 3rd year"
    m_to_year = re.search(r'\bto\s+([1-5](?:st|nd|rd|th)?(?:\s+year)?|first(?:\s+year)?|second(?:\s+year)?|third(?:\s+year)?|fourth(?:\s+year)?|final(?:\s+year)?|postgraduate|phd)\b', lower)
    if m_to_year:
        year_target = m_to_year.group(1).strip()
    
    if not year_target:
        m_year_direct = re.search(r'\byear(?:\s+of\s+study)?\s*(?:to|as|=)\s*([1-5](?:st|nd|rd|th)?(?:\s+year)?|first|second|third|fourth|final|postgraduate|phd)\b', lower)
        if m_year_direct:
            year_target = m_year_direct.group(1).strip()

    if not year_target and any(k in lower for k in ["change my year", "update my year", "edit my year", "modify my year"]):
        # Look for target year word
        for word in ["1st year", "2nd year", "3rd year", "4th year", "3rd", "2nd", "1st", "4th", "first year", "second year", "third year", "fourth year"]:
            if word in lower:
                year_target = word
                break

    if year_target:
        norm_year = normalize_year_of_study(year_target)
        if norm_year:
            updates["year_of_study"] = norm_year

    # 2. Department:
    # "change department from Robotics And Automation to Computer Science Engineering"
    # "change my department to Mechanical Engineering", "dept to Computer Science", "department to Robotics and Automation in my profile"
    m_dept = re.search(r'\b(?:department|dept|major)(?:[^\n]*?)\b(?:to|as|=)\s*([a-zA-Z\s&]+?)(?:\s+in\s+(?:my\s+profile|the\s+profile|profile)|\s+for\s+my\s+profile|[.?!;]|$)', text, re.IGNORECASE)
    if m_dept:
        dept_val = m_dept.group(1).strip()
        dept_val = re.sub(r'\s+(?:please|now|immediately)$', '', dept_val, flags=re.IGNORECASE).strip()
        if len(dept_val) >= 2 and dept_val.lower() not in ["to", "the", "my"]:
            updates["department"] = dept_val.title()

    # 3. Phone / Contact:
    # "change phone from 1234567890 to +91 9876543210", "contact number to 9876543210"
    m_phone = re.search(r'\b(?:phone|mobile|contact)(?:[^\n]*?)\b(?:to|as|=)\s*([+\d\s\-()]{7,20})', text, re.IGNORECASE)
    if m_phone:
        updates["phone"] = m_phone.group(1).strip()

    # 4. College / University:
    # "change college from MIT to Stanford University", "college name to MIT"
    m_college = re.search(r'\b(?:college|university)(?:[^\n]*?)\b(?:to|as|=)\s*([a-zA-Z0-9\s&.,]+?)(?:\s+in\s+(?:my\s+profile|the\s+profile|profile)|[.?!;]|$)', text, re.IGNORECASE)
    if m_college:
        col_val = m_college.group(1).strip()
        col_val = re.sub(r'\s+(?:please|now|immediately)$', '', col_val, flags=re.IGNORECASE).strip()
        if len(col_val) >= 2 and col_val.lower() not in ["to", "the", "my"]:
            updates["college_name"] = col_val

    # 5. Roll / Student ID Number:
    # "change student id from OLD to CS-101", "roll number to 2024CS01"
    m_roll = re.search(r'\b(?:student\s*id|roll(?:\s*(?:number|no))?)(?:[^\n]*?)\b(?:to|as|=)\s*([a-zA-Z0-9\-_/]+)', text, re.IGNORECASE)
    if m_roll:
        updates["student_id_number"] = m_roll.group(1).strip().upper()

    # 6. Full Name:
    # Must explicitly refer to user/student name ("my name", "full name", "user name", "student name",
    # or "change name / edit name / update name") and NOT university/college name.
    has_institution_name = bool(re.search(r'\b(?:college|university|school|dept|department|event|team)\s*name\b', text, re.IGNORECASE))

    m_name = re.search(r'\b(?:my\s+name|full\s+name|user\s+name|student\s+name|(?:change|update|edit|set|modify)\s+name)(?:[^\n]*?)\b(?:to|as|=)\s*([a-zA-Z\s]{2,50})(?:\s+in\s+(?:my\s+profile|the\s+profile|profile)|[.?!;]|$)', text, re.IGNORECASE)

    if m_name and not has_institution_name:
        name_val = m_name.group(1).strip()
        name_val = re.sub(r'\s+(?:please|now|immediately)$', '', name_val, flags=re.IGNORECASE).strip()
        if len(name_val) >= 2 and name_val.lower() not in ["to", "the", "alex", "vit", "mit", "university", "college"]:
            updates["full_name"] = name_val.title()

    return updates


def update_student_profile(
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    updates: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Executes actual student profile update in SQLite database.
    Updates User and StudentProfile rows and records an audit log entry.
    """
    if not updates:
        return {
            "success": False,
            "error": "NO_UPDATES_PROVIDED",
            "message": "No profile fields were provided to update."
        }

    try:
        from app.db.session import SessionLocal
        from app.models.user import User, StudentProfile
        from app.services.audit_service import log_action

        db = SessionLocal()
        try:
            # 1. Resolve User
            user = None
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
            if not user and user_email:
                user = db.query(User).filter(User.email.ilike(user_email.strip())).first()

            if not user:
                return {
                    "success": False,
                    "error": "NOT_LOGGED_IN",
                    "message": "You must be signed into your student account to update your profile. Please sign in at [/login](/login)."
                }

            # 2. Track changes for audit and response
            old_values: Dict[str, Any] = {}
            new_values: Dict[str, Any] = {}
            changed_summary: List[str] = []

            # User model fields
            if "full_name" in updates and updates["full_name"]:
                old_values["full_name"] = user.full_name
                user.full_name = updates["full_name"]
                new_values["full_name"] = user.full_name
                changed_summary.append(f"• **Name**: `{user.full_name}` *(was {old_values['full_name']})*")

            if "phone" in updates and updates["phone"]:
                old_values["phone"] = user.phone or "Not set"
                user.phone = updates["phone"]
                new_values["phone"] = user.phone
                changed_summary.append(f"• **Phone**: `{user.phone}` *(was {old_values['phone']})*")

            # StudentProfile model fields
            student_profile = user.student_profile
            if not student_profile:
                student_profile = StudentProfile(
                    user_id=user.id,
                    college_name=updates.get("college_name", "Fest University"),
                    student_id_number=updates.get("student_id_number", f"STU-{user.id:04d}"),
                    department=updates.get("department", "Computer Science"),
                    year_of_study=updates.get("year_of_study", "1st Year")
                )
                db.add(student_profile)
                db.flush()
                old_values["student_profile"] = "Created new profile"
            
            if "year_of_study" in updates and updates["year_of_study"]:
                old_year = student_profile.year_of_study
                old_values["year_of_study"] = old_year
                student_profile.year_of_study = updates["year_of_study"]
                new_values["year_of_study"] = student_profile.year_of_study
                changed_summary.append(f"• **Year of Study**: `{student_profile.year_of_study}` *(was {old_year})*")

            if "department" in updates and updates["department"]:
                old_dept = student_profile.department
                old_values["department"] = old_dept
                student_profile.department = updates["department"]
                new_values["department"] = student_profile.department
                changed_summary.append(f"• **Department**: `{student_profile.department}` *(was {old_dept})*")

            if "college_name" in updates and updates["college_name"]:
                old_col = student_profile.college_name
                old_values["college_name"] = old_col
                student_profile.college_name = updates["college_name"]
                new_values["college_name"] = student_profile.college_name
                changed_summary.append(f"• **College**: `{student_profile.college_name}` *(was {old_col})*")

            if "student_id_number" in updates and updates["student_id_number"]:
                old_id = student_profile.student_id_number
                old_values["student_id_number"] = old_id
                student_profile.student_id_number = updates["student_id_number"]
                new_values["student_id_number"] = student_profile.student_id_number
                changed_summary.append(f"• **Student ID**: `{student_profile.student_id_number}` *(was {old_id})*")

            if not new_values:
                return {
                    "success": False,
                    "error": "NO_RECOGNIZED_FIELDS",
                    "message": "Could not identify which profile fields to update. You can update your **Year of Study**, **Department**, **Phone Number**, **College Name**, or **Student ID**."
                }

            db.commit()
            db.refresh(user)
            if user.student_profile:
                db.refresh(user.student_profile)

            # Record audit log
            try:
                log_action(
                    db=db,
                    action="PROFILE_UPDATED",
                    entity_type="User",
                    entity_id=str(user.id),
                    user_id=user.id,
                    old_values=old_values,
                    new_values=new_values
                )
            except Exception:
                pass

            changes_text = "\n".join(changed_summary)
            current_year = user.student_profile.year_of_study if user.student_profile else "N/A"
            current_dept = user.student_profile.department if user.student_profile else "N/A"
            current_col = user.student_profile.college_name if user.student_profile else "N/A"

            msg = (
                f"### ✅ Profile Updated & Saved Successfully!\n\n"
                f"Your student profile in our database has been updated:\n\n"
                f"{changes_text}\n\n"
                f"**Current Profile Summary**:\n"
                f"• **Student**: {user.full_name} (`{user.email}`)\n"
                f"• **Academic Year**: {current_year}\n"
                f"• **Department**: {current_dept}\n"
                f"• **College / University**: {current_col}\n\n"
                f"Your changes are live across the portal. You can also view or edit anytime at [Student Profile](/student/profile)."
            )

            return {
                "success": True,
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "old_values": old_values,
                "new_values": new_values,
                "year_of_study": current_year,
                "department": current_dept,
                "message": msg
            }

        finally:
            db.close()

    except Exception as e:
        return {
            "success": False,
            "error": "DB_ERROR",
            "message": f"Failed to save profile update to database: {str(e)}"
        }


def get_student_profile(
    user_id: Optional[int] = None,
    user_email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetches the student profile from the database for display.
    """
    try:
        from app.db.session import SessionLocal
        from app.models.user import User

        db = SessionLocal()
        try:
            user = None
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
            if not user and user_email:
                user = db.query(User).filter(User.email.ilike(user_email.strip())).first()

            if not user:
                return {
                    "success": False,
                    "message": "Please sign in to inspect your profile details at [/login](/login)."
                }

            sp = user.student_profile
            year_val = sp.year_of_study if sp else "Not specified"
            dept_val = sp.department if sp else "Not specified"
            col_val = sp.college_name if sp else "Not specified"
            id_val = sp.student_id_number if sp else "Not specified"

            msg = (
                f"### 🎓 Your Student Profile\n\n"
                f"• **Full Name**: **{user.full_name}**\n"
                f"• **Email**: `{user.email}`\n"
                f"• **Role**: `{user.role.value if hasattr(user.role, 'value') else user.role}`\n"
                f"• **Phone**: `{user.phone or 'Not set'}`\n"
                f"• **Year of Study**: **{year_val}**\n"
                f"• **Department**: **{dept_val}**\n"
                f"• **College / University**: {col_val}\n"
                f"• **Student ID / Roll**: `{id_val}`\n\n"
                f"💡 *Need to make a change? Just say 'Change my year to 3rd year' or 'Update my department to Robotics'!*"
            )

            return {
                "success": True,
                "user_id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "year_of_study": year_val,
                "department": dept_val,
                "college_name": col_val,
                "student_id_number": id_val,
                "message": msg
            }

        finally:
            db.close()

    except Exception as e:
        return {
            "success": False,
            "message": f"Unable to fetch profile: {str(e)}"
        }
