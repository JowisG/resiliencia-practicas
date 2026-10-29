import json
import pandas as pd

# --- GitHub Dependabot ---
with open("alertas.json", encoding="utf-16") as f:
    alertas = pd.json_normalize(json.load(f))

dep = alertas[
    [
        "number",
        "state",
        "security_advisory.ghsa_id",
        "security_advisory.cve_id",
        "dependency.package.name",
        "dependency.manifest_path",
        "security_advisory.severity",
    ]
].copy()

# Renombrar columnas para trabajar más cómodamente
dep = dep.rename(columns={
    "security_advisory.ghsa_id": "ghsa",
    "security_advisory.cve_id": "cve",
    "dependency.package.name": "paquete",
    "dependency.manifest_path": "fichero",
    "security_advisory.severity": "severidad_github",
})

# Normalizar para comparar sin problemas de mayúsculas/minúsculas
dep["clave_paquete"] = dep["paquete"].str.strip().str.lower()
dep["clave_cve"] = dep["cve"].str.strip().str.upper()


# --- Trivy ---
with open("trivy.json", encoding="utf-8") as f:
    t = json.load(f)

filas = [
    {
        "id": v["VulnerabilityID"],
        "paquete": v["PkgName"],
        "version": v["InstalledVersion"],
        "severidad": v["Severity"],
        "fichero": r["Target"],
    }
    for r in t.get("Results", [])
    for v in (r.get("Vulnerabilities") or [])
]

trivy = pd.DataFrame(filas)

# Normalizar las claves de comparación
trivy["clave_paquete"] = trivy["paquete"].str.strip().str.lower()
trivy["clave_cve"] = trivy["id"].str.strip().str.upper()


# --- Resumen inicial ---
print("Alertas cargadas de GitHub:", len(alertas))
print("Dependencias/alertas seleccionadas:", len(dep))
print("Vulnerabilidades de Trivy:", len(trivy))


# --- Alertas de GitHub que no están en Trivy ---
comparacion = dep.merge(
    trivy[["clave_paquete", "clave_cve"]],
    on=["clave_paquete", "clave_cve"],
    how="left",
    indicator=True,
)

solo_github = (
    comparacion[comparacion["_merge"] == "left_only"]
    .drop(columns=["_merge", "clave_paquete", "clave_cve"])
    .sort_values(["paquete", "cve"])
)

print("\n=== Detectadas por GitHub pero no por Trivy ===")
print("Total:", len(solo_github))

print(
    solo_github[
        ["number", "state", "ghsa", "cve", "paquete", "severidad_github", "fichero"]
    ].to_string(index=False)
)

# Opcional: guardar el resultado
solo_github.to_csv(
    "github_no_trivy.csv",
    index=False,
    encoding="utf-8-sig"
)


# --- Los 5 paquetes con más avisos de GitHub ---
top_5_github = (
    dep.groupby("paquete")
    .agg(
        alertas=("number", "count"),
        avisos_ghsa=("ghsa", "nunique"),
        cves=("cve", "nunique"),
    )
    .sort_values(["avisos_ghsa", "alertas"], ascending=False)
    .head(5)
    .reset_index()
)

print("\n=== Top 5 paquetes con más avisos en GitHub ===")
print(top_5_github.to_string(index=False))


# 1. Alertas frente a avisos distintos en cada fuente 
# Las alertas que hay en github son 163 frente a las 157 de trivy. En cuanto a los avisos son 156 en github y 150 en trivy, por lo que las 6 alertas que detecta github son 6 nuevos avisos. 

# 2. Qué encuentra una fuente y no la otra (cuidado: Dependabot usa GHSA y Trivy suele usar CVE) 
# GitHub Dependabot encuentra estas 6 CVE que no encuentra trivy:
# Total: 6
#  number state                ghsa            cve                                       paquete severidad fichero
#      49  open GHSA-pfh2-hfmq-phg5 CVE-2023-51074                 com.jayway.jsonpath:json-path    medium pom.xml
#       5  open GHSA-v528-7hrm-frqp CVE-2021-27568                        net.minidev:json-smart    medium pom.xml
#      24  open GHSA-493p-pfq6-5258  CVE-2023-1370                        net.minidev:json-smart      high pom.xml
#      93  open GHSA-rqfh-9r24-8c9r CVE-2026-24400                      org.assertj:assertj-core      high pom.xml
#     108  open GHSA-56v8-86gj-66jp CVE-2026-40972 org.springframework.boot:spring-boot-devtools      high pom.xml
#      48  open GHSA-chfm-68vv-pvw5 CVE-2024-31573                      org.xmlunit:xmlunit-core       low pom.xml

# 3. Los cinco paquetes que concentran más avisos
#                                     paquete  alertas  avisos_ghsa  cves
#   org.apache.tomcat.embed:tomcat-embed-core       43           43    43
#           org.springframework:spring-webmvc       18           18    18
# com.fasterxml.jackson.core:jackson-databind       15           15    15
#                 ch.qos.logback:logback-core        8            8     8
#       org.springframework:spring-expression        8            8     8