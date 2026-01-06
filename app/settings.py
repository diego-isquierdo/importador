from __future__ import annotations

import os


class Settings:
    def __init__(self) -> None:
        self.movidesk_base_url = os.getenv("MOVIDESK_BASE_URL", "https://api.movidesk.com/public/v1")
        self.upload_dir = os.getenv("UPLOAD_DIR", "uploads")
        self.job_dir = os.getenv("JOB_DIR", "jobs")
        self.log_dir = os.getenv("LOG_DIR", "logs")
        self.rate_limit_seconds = int(os.getenv("RATE_LIMIT_SECONDS", "6"))

        self.enterprise_created_by_id = os.getenv("ENTERPRISE_CREATED_BY_ID", "1592146388")
        # Default Empresas baseado em JSON validado fornecido
        self.empresas_created_by_id = os.getenv("EMPRESAS_CREATED_BY_ID", "252142226")

        self.enterprise_service_first_level_id = int(os.getenv("ENTERPRISE_SERVICE_FIRST_LEVEL_ID", "207559"))
        # Default Empresas baseado em JSON validado fornecido
        self.empresas_service_first_level_id = int(os.getenv("EMPRESAS_SERVICE_FIRST_LEVEL_ID", "545682"))

        self.enterprise_service_first_level = os.getenv("ENTERPRISE_SERVICE_FIRST_LEVEL", "Atividades Internas")
        self.empresas_service_first_level = os.getenv("EMPRESAS_SERVICE_FIRST_LEVEL", "Atividades Internas")

        self.enterprise_service_second_level = os.getenv(
            "ENTERPRISE_SERVICE_SECOND_LEVEL", "3. Serviços (uso interno da ProJuris)"
        )
        # Default Empresas baseado em JSON validado fornecido
        self.empresas_service_second_level = os.getenv("EMPRESAS_SERVICE_SECOND_LEVEL", "Implantação de Serviços")

        self.enterprise_service_third_level = os.getenv("ENTERPRISE_SERVICE_THIRD_LEVEL", "")
        self.empresas_service_third_level = os.getenv(
            "EMPRESAS_SERVICE_THIRD_LEVEL", "2. Serviços (uso internos da PROJURIS)"
        )

        # serviceFull pode não ser simplesmente (second, first) dependendo do catálogo de serviços
        self.enterprise_service_full_0 = os.getenv(
            "ENTERPRISE_SERVICE_FULL_0", "3. Serviços (uso interno da ProJuris)"
        )
        self.enterprise_service_full_1 = os.getenv("ENTERPRISE_SERVICE_FULL_1", "Atividades Internas")

        self.empresas_service_full_0 = os.getenv(
            "EMPRESAS_SERVICE_FULL_0", "3. Serviços (uso interno da ProJuris)"
        )
        self.empresas_service_full_1 = os.getenv("EMPRESAS_SERVICE_FULL_1", "Atividades Internas")

        self.enterprise_organization_id = os.getenv("ENTERPRISE_ORGANIZATION_ID", "1419498004")
        self.empresas_organization_id = os.getenv("EMPRESAS_ORGANIZATION_ID", "1115455417")

        self.enterprise_organization_business_name = os.getenv("ENTERPRISE_ORGANIZATION_BUSINESS_NAME", "ProJuris")
        self.empresas_organization_business_name = os.getenv(
            "EMPRESAS_ORGANIZATION_BUSINESS_NAME", "PROJURIS - interno"
        )


def get_settings() -> Settings:
    return Settings()
