# Security

## Aceptación temporal de riesgo: GHSA-g5vr-rgqm-vf78 / CVE-2024-38819

- **Fecha de decisión:** 2026-10-27
- **Componente afectado:** `org.springframework:spring-webmvc:5.3.2`
- **Severidad:** alta
- **Estado:** riesgo aceptado temporalmente
- **Remediación definitiva prevista:** migrar a Spring Boot 3.x con Java 17 y Spring Framework 6.1.14 o superior.

### Origen y alcance

La aplicación usa `org.springframework.boot:spring-boot-starter-web:2.4.1`, que incorpora de forma transitiva
`org.springframework:spring-webmvc:5.3.2` con alcance de compilación. Por tanto, la biblioteca se incluye en el
artefacto ejecutable de Spring Boot.

La vulnerabilidad afecta a aplicaciones Spring MVC que usan rutas funcionales (`RouterFunctions`) con recursos del
sistema de ficheros (`FileSystemResource`).

### Evaluación de exposición

La revisión del código y de la configuración del repositorio no ha encontrado:

- Uso de `RouterFunctions`, `RouterFunction` o `HandlerFunction`.
- Uso de `FileSystemResource`.
- Configuración de recursos desde ubicaciones `file:` o `filesystem:`.
- Personalizaciones de manejadores de recursos mediante `WebMvcConfigurer` o `ResourceHandlerRegistry`.

Los recursos estáticos de la aplicación se empaquetan desde `src/main/resources/static`; no se sirven desde el
sistema de ficheros. Por ello, el flujo específico afectado por CVE-2024-38819 no está habilitado en la versión
actual de la aplicación.

### Motivo de la aceptación

Spring Framework 5.3 finaliza en la versión 5.3.39. No existe una versión publicada 5.3.42 ni una corrección
disponible en la rama 5.3 para esta vulnerabilidad. La corrección indicada por Trivy es Spring Framework 6.1.14,
que requiere la migración a Spring Boot 3.x y Java 17.

Forzar Spring Framework 6.1.14 sobre Spring Boot 2.4.1 no es una solución soportada debido a las incompatibilidades
de Spring 6 con la plataforma `javax.*` y al cambio a `jakarta.*`.

### Controles compensatorios

1. No introducir rutas funcionales de Spring MVC combinadas con `FileSystemResource` o recursos `file:`/`filesystem:`
   sin reevaluar esta vulnerabilidad.
2. No configurar recursos estáticos externos al artefacto sin una revisión de seguridad.
3. Revisar esta aceptación de riesgo al planificar o ejecutar la migración a Spring Boot 3.x y Java 17.
4. Mantener el análisis de dependencias y vulnerabilidades en el proceso de integración continua.

### Plan de remediación

Migrar la aplicación desde Spring Boot 2.4.1 a Spring Boot 3.x, elevar el runtime a Java 17 y adaptar las APIs
necesarias de `javax.*` a `jakarta.*`. La versión objetivo debe gestionar Spring Framework 6.1.14 o superior para
eliminar CVE-2024-38819.
