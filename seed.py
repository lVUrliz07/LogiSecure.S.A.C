import os
import sys

# Add current path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, init_db
from app.models import User, RoleEnum, Ruta
from datetime import datetime, timedelta
import bcrypt

def seed_db():
    init_db()  # Ensure tables exist
    db = SessionLocal()
    
    # 1. Insert Choferes
    for i in range(1, 4):
        username = f"chofer_seed{i}"
        user = db.query(User).filter(User.username == username).first()
        if not user:
            new_chofer = User(
                email=f"{username}@logisecure.com",
                username=username,
                hashed_password=bcrypt.hashpw(b"password", bcrypt.gensalt()).decode("utf-8"),
                full_name=f"Chofer Ejemplo {i}",
                role=RoleEnum.CHOFER,
                is_active=True
            )
            db.add(new_chofer)
            
    # 2. Insert Dispatcher
    disp_username = "dispatcher_seed1"
    dispatcher = db.query(User).filter(User.username == disp_username).first()
    if not dispatcher:
        new_disp = User(
            email=f"{disp_username}@logisecure.com",
            username=disp_username,
            hashed_password=bcrypt.hashpw(b"password", bcrypt.gensalt()).decode("utf-8"),
            full_name="Dispatcher Principal",
            role=RoleEnum.DISPATCHER,
            is_active=True
        )
        db.add(new_disp)

    db.commit()

    # 3. Create Rutas
    chofer = db.query(User).filter(User.role == RoleEnum.CHOFER).first()
    if chofer:
        rutas_data = [
            {"origen": "Almacén Central", "destino": "Sucursal Norte", "estado": "en_progreso", "distancia_km": 45.5},
            {"origen": "Puerto", "destino": "Almacén Central", "estado": "completada", "distancia_km": 120.0},
            {"origen": "Sucursal Sur", "destino": "Cliente Final", "estado": "pendiente", "distancia_km": 12.3},
            {"origen": "Fábrica", "destino": "Sucursal Este", "estado": "en_progreso", "distancia_km": 88.0},
            {"origen": "Almacén Central", "destino": "Cliente Corporativo", "estado": "completada", "distancia_km": 5.5},
        ]
        
        for data in rutas_data:
            ruta = db.query(Ruta).filter(Ruta.origen == data["origen"], Ruta.destino == data["destino"], Ruta.estado == data["estado"]).first()
            if not ruta:
                new_ruta = Ruta(
                    chofer_id=chofer.id,
                    origen=data["origen"],
                    destino=data["destino"],
                    estado=data["estado"],
                    distancia_km=data["distancia_km"]
                )
                db.add(new_ruta)
        
        db.commit()

    print("Datos semilla insertados correctamente.")
    db.close()

if __name__ == "__main__":
    seed_db()
