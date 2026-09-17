from app.services.connection_profile_service import ConnectionProfileService

service = ConnectionProfileService()

service.create_profile(
    name="Suricato Local",
    server="127.0.0.1",
    database="suricato",
    username="suricato",
    tables=[
        "TbLogService",
        "TbComanAcess"
    ]
)

profiles = service.load_profiles()

print("Perfis encontrados:\n")

for profile in profiles:
    print(f"Nome: {profile.name}")
    print(f"Servidor: {profile.server}")
    print(f"Banco: {profile.database}")
    print(f"Usuário: {profile.username}")
    print(f"Tabelas: {', '.join(profile.tables)}")
    print("-" * 40)