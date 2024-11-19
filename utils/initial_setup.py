from sqlalchemy.orm import Session
from models.models import Admin
from utils.auth import get_password_hash

def create_initial_admin(db: Session):
    # Verificar si ya existe un admin
    admin = db.query(Admin).filter(Admin.email == "admin@admin.com").first()
    
    if admin:
        return admin
        
    # Crear admin inicial
    admin = Admin(
        email="admin@admin.com",
        hashed_password=get_password_hash("password1313"),
        full_name="Administrador Principal"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print("\n=== Usuario Administrador Registrado ===")
    print(f"Email: {admin.email}")
    print(f"Nombre: {admin.full_name}")
    print("Contraseña: password1313")
    print("======================================\n")
    return admin