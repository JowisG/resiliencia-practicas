# Día 2: GitHub, herramientas y agentes

## Índice
1. [Lab 4](#1-lab-4)
2. [Lab 6](#2-lab-6)
3. [Lab 8](#3-lab-8)
4. [PRs](#4-prs)
5. [Autocomprobación](#5-autocomprobación)

## 1. Lab 4
En su mayoría si coinciden, GitHub tiene 163 vulnerabilidades (14 Low, 65 Moderate, 61 High, 23 Critical) encontradas, mientras trivy a encontrado 157 vulnerabilidades (13 low, 63 Medium, 58 High, 23 Critical), eso por las alertas. En cuanto a los avisos, github tiene 156 y trivy tiene 150. Por lo que se puede ver qeu GitHub detecta 6 más.

## 2. Lab 6
Gitleaks no me dice que tenga "leaks" por mucho que intente probar tokens de github u otras claves secretas de todas formas contesto según lo que debería pasar.

**¿Por qué el segundo escaneo sigue encontrando el secreto?**
Porque el archivo esta en un commit anterior, es decir, si alguien regresa a ese commit sigue pudiendo acceder a esas claves secretas por lo que gitleaks no solo revisa los archivos que hay en el commit actual so no tambien los pasados.

**¿Por qué borrarlo no basta y quién tiene que rotarlo?**
Como ya he dicho sigue siendo accesible si se vuelve al commit pasado, a menos que borres el commit en sí. La persona que o rota suele ser un administrador o alguien de seguridad que se encarga de manejar el acceso a las claves secretas y su rotación.

**¿Qué cambiarías para que no vuelva a pasar?** (Pista: gestor de secretos y una regla antes del commit.)
Primero lo podría en .gitignore para que el archivo sea ignorado por git, luego para evitar cualquier incidente con el .gitignore se puede poner GitLeaks como pre-commit, es decir, que se ejecute GitLeaks cuando hagamos un commit y bloquee los que puedan tener leaks.

## 3. Lab 8

<table>
    <table style="border: 1px solid white">
    <tr >
        <th style="border-bottom: 1px solid white">Alerta</th>
        <td style="border-bottom: 1px solid white">
            Número: #155
            <br>GHSA-g5vr-rgqm-vf78
            <br>org.springframework:spring-webmvc 5.3.2
        </td>
    </tr>
    <tr>
        <th style="border-bottom: 1px solid white">Herramienta</th>
        <td style="border-bottom: 1px solid white">aXet.Plugin 3.0.0, modelo GPT-5.6 Terra</td>
    </tr>
    <tr>
        <th style="border-bottom: 1px solid white">Instrucciones</th>
        <td style="border-bottom: 1px solid white">
            En este repositorio hay una alerta de Dependabot sobre org.springframework:spring-webmvc 5.3.2 (GHSA-g5vr-rgqm-vf78).
            <br><br>
            1. Analiza de dónde viene la dependencia y si llega al artefacto desplegado. <br>
            2. Propón un plan de corrección en el origen, sin overrides ni exclusiones si se puede evitar (Mira a ver si hay una versión con la corrección y si se puede subir el padre de manera limpia a una versión que contenga esa versión corregida o si es más limpio subir directamente la transitiva, si es que es transitiva).<br>
            3. No modifiques ningún fichero hasta que yo apruebe el plan. <br>
            4. Cuando lo apruebe: aplica el cambio, ejecuta "./mvnw clean verify" y vuelve a escanear con trivy (trivy fs --scanners vuln .). <br>
            5. Resume el plan por puntos no muy extendidos, teniendo en cuenta sobre todo: artefacto a subir, porque se sube y que afecta, se sube a una versión que corrige la vulnerabilidad y porque.<br>
            6. Tras eso dime los siguientes pasos que vas ha hacer, y considerare s continuas o darte feedback.
            <br><br>
            Recuerda que para powershell necesitas ejecutar ./mvnw dependency:tree -Dincludes=grupo:artefacto
            Vas a necesitar las comilla en:
            ./mvnw dependency:tree "-Dincludes=grupo:artefacto"
            Ya que si no saldrá un error debido a que los "." separan el comando.
            <br>
            Otro promt:
            Antes de nada, si ejecutas trivy antes de hacer cambios y busca la vulnerabilidad, te dice que la versión que tiene corregida el cambio es 6.1.14 y no la 5.13.41. Te paso el archivo con la salida de trivy
            <br>
            Otro promt:
            Aprobar Spring Framework 5.3.42
            <br>
            Al no existir Spring Framework 5.3.42, y se necesita actualizar a la versión 6.1.14 que usa Spring Boot 3 que usa Java 17, no que da más que subir de versión o asumir el riesgo hasta que se suba la versión. Decido que se acepta el riesgo y se documenta para cuando se suba a la versión de Spring Boot 3.
        </td>
    </tr>
    <tr>
        <th style="border-bottom: 1px solid white">Plan propuesto</th>
        <td style="border-bottom: 1px solid white">
- Origen: org.springframework:spring-webmvc:5.3.2 es una dependencia transitiva de producción:

 ```text
 spring-petclinic
 └─ spring-boot-starter-web:2.4.1
    └─ spring-webmvc:5.3.2 (compile)
 ```

- Artefacto desplegado: sí llega al JAR ejecutable. compile hace que esté disponible en runtime y el spring-boot-maven-plugin empaqueta las dependencias de runtime bajo BOOT-INF/lib/.

- Vulnerabilidad: GHSA-g5vr-rgqm-vf78 (CVE-2024-38819) afecta a Spring MVC <= 5.3.40. La primera versión corregida de la rama 5.3 es __`5.3.41`__.

- __Padre actual:__ `spring-boot-starter-parent:2.4.1` gestiona Spring Framework `5.3.2`.

- __Alternativa mediante padre:__ no existe un salto limpio solo de padre dentro de Spring Boot 2.x que llegue a `5.3.41`:

 - Spring Boot `2.4.2` gestiona Spring Framework `5.3.3`.
 - Spring Boot `2.7.18` —último 2.x y aún compatible con Java 8— gestiona `5.3.31`, que sigue afectada.
 - Boot 3.x cambia a Spring 6 y exige Java 17, además de una migración Jakarta; no es una corrección acotada para esta alerta.

### Plan propuesto

1. __Subir la propiedad gestionada `spring-framework.version` a `5.3.41`__ en `pom.xml`.

  - Se gestiona desde el padre Boot y actualiza de manera alineada todos los módulos `org.springframework` de la aplicación, incluido `spring-webmvc`.
  - Es preferible a declarar `spring-webmvc` directamente o excluir/reinyectar dependencias: evita mezclar `spring-webmvc:5.3.41` con `spring-core`, `spring-web`, `spring-beans`, etc. en `5.3.2`.
  - Es una excepción de gestión necesaria porque el padre 2.x no alcanza una versión corregida; no hay una actualización de padre compatible y suficiente.

2. __Efecto sobre el artefacto:__ el JAR desplegable pasará a incluir `spring-webmvc-5.3.41.jar` —y el resto de Spring Framework 5.3.41— bajo `BOOT-INF/lib`, eliminando la versión afectada `5.3.2`.

3. __Validación posterior a tu aprobación:__

  - Aplicar únicamente ese cambio de versión.

  - Ejecutar, mediante PowerShell por compatibilidad del entorno:

    ```powershell
    & .\mvnw clean verify
    ```

  - Confirmar la versión resuelta:

    ```powershell
    & .\mvnw dependency:tree '-Dincludes=org.springframework:spring-webmvc'
    ```

  - Ejecutar:

    ```powershell
    trivy fs --scanners vuln .
    ```

  - Informar de los resultados, distinguiendo la alerta objetivo de los demás hallazgos históricos que el escaneo ya identifica.

<br>
Trivy se ha ejecutado antes de cualquier cambio: detecta 157 vulnerabilidades y para CVE-2024-38819/GHSA-g5vr-rgqm-vf78 muestra únicamente `6.1.14`. He contrastado el aviso oficial de GitHub: la misma vulnerabilidad está corregida también en la rama 5.3 a partir de `5.3.41`; Trivy omite esa rama en su base de datos, por lo que su columna «Fixed Version» no es exhaustiva. Además, subir solo a 5.3.41 dejaría otra alerta de `spring-webmvc` (CVE-2024-38828) que Trivy corrige en `5.3.42`. Propongo ajustar el plan para definir `spring-framework.version` en `5.3.42`: mantiene compatibilidad con Spring Boot 2.4/Java 8, actualiza de forma coherente todos los módulos Spring 5.3.x y corrige ambas vulnerabilidades de Spring MVC. ¿Apruebas este plan ajustado?
<br>
No existe versión 5.3.40 o superior.
- Se descarta Spring Framework 5.3.42: Maven Central confirma que no existe. La rama 5.3 termina en 5.3.39.

- Por tanto, no hay parche publicable en Spring Framework 5.3 para `GHSA-g5vr-rgqm-vf78` / CVE-2024-38819.

- Trivy es correcto en este caso: la ruta corregida publicada es Spring Framework 6.1.14.

- La corrección requiere una migración mayor:

  1. Subir el padre `org.springframework.boot:spring-boot-starter-parent` de `2.4.1` a una versión Boot 3.x que gestione Spring Framework `6.1.14` (por ejemplo, Boot 3.3.8).
  2. Elevar `java.version` de 8 a 17, requisito de Spring Boot 3.
  3. Adaptar el código y dependencias de `javax.*` a `jakarta.*` donde aplique, además de resolver incompatibilidades de APIs/configuración derivadas de Boot 3.
  4. Ejecutar `./mvnw clean verify`, confirmar `spring-webmvc:6.1.14` y repetir Trivy.

<br>
La decisión queda registrada para el plan:

- Se acepta temporalmente el riesgo de __GHSA-g5vr-rgqm-vf78 / CVE-2024-38819__.
- No existe una versión `5.3.42`; Spring Framework 5.3 finaliza en `5.3.39` y no ofrece parche para esta vulnerabilidad.
- La corrección soportada requiere `spring-webmvc:6.1.14`, que implica migrar a Spring Boot 3.x y Java 17.
- La aplicación no utiliza `RouterFunctions` ni `FileSystemResource`, por lo que no emplea el flujo afectado por esta vulnerabilidad.
- El POM permanece sin cambios.
- La remediación definitiva queda condicionada a la futura migración a Spring Boot 3.x / Java 17.

Para documentarlo en el repositorio necesito concretar el destino del registro. Crear un documento SECURITY.md
        </td>
    </tr>
    <tr>
        <th style="border-bottom: 1px solid white">Cambios aplicados</th>
        <td style="border-bottom: 1px solid white">Creado un archivo SERCURITY.md con las razones por las que se va a aceptar el riego.</td>
    </tr>
    <tr>
        <th style="border-bottom: 1px solid white">Verificación</th>
        <td style="border-bottom: 1px solid white">Build: correcto, Tests: correcto, re-escaneo: correcto, pipeline: correcto, alerta: abierta</td>
    </tr>
    <tr>
        <th style="border-bottom: 1px solid white">Errores o riesgos</th>
        <td style="border-bottom: 1px solid white">Pues ha pensado que existia una versión de Spring Framework, le he mencionado que se vijase en trivy ya que tiene la versión que tiene la vulnerabilidad corregida, aun así insitio en la existencia de esa libreria y por tanto fallo y tuvo que hacer otro plan.</td>
    </tr>
    <tr>
        <th style="border-bottom: 1px solid white">Tiempos</th>
        <td style="border-bottom: 1px solid white">
Lab 5:
- Análisis: 40min 
- Cambio: 1min
- Verificación: 2min 46s
- PR y cierre: 14min

Lab 8:
- Análisis: ~1h
- Cambio: 1min
- Verificación: 1min
- PR y cierre: 4min (Se debe a que el ./mvnw verify ya tenia todo descargado y tardo menos)
        </td>
    </tr>
    <tr>
        <th style="border-bottom: 1px solid white">Consumo</th>
        <td style="border-bottom: 1px solid white">No dice</td>
    </tr>
    <tr>
        <th style="border-bottom: 1px solid white">Conclusión</th>
        <td style="border-bottom: 1px solid white">Suele aportar una mejor explicación y más detalles sobre como se puede resolver las vulnerabilidades de dependecias, tambien da muchos caminos para resolverla lo cual ayuda a evaluar y dar con la mejor opción.</td>
    </tr>
</table>
</table>

## 4. PRs
**Lab 5**: https://github.com/JowisG/resiliencia-practicas/pull/1

**Lab 8**: https://github.com/JowisG/resiliencia-practicas/pull/2

## 5. Autocomprobación

1. **¿En qué dos momentos interviene una persona en el ciclo de remediación, y por qué son dos y no uno?**

Se interviene cuando se hace commit, para comprobar que lo que se ha realizado este bien y no rompa el proyecto, y cuando se hace una PR, para evitar que no se va integrar errores en el proyecto. Es decir, se revisa para cuando se hacen cambios, comprobando que se haya realizado bien, y cuando se quieran integrar esos cambios, para ver que se integre bien con el resto del proyecto.

2. **¿Qué diferencia hay entre que el agente diga «corregido» y que la herramienta de seguridad cierre la alerta?**

Que un agente diga *corregido* solo significa que al error que estaba corrigiendo se le ha aplicado un arreglo, pero no necesariamente esta corregido. Si una herramienta de seguridad cierra la alerta quiere decir que tras pasar un escaneo para comprobar las vulnerabilidades de nuevo y ve que realmente ya no esta la vulnerabilidad, entonces se cierra la alerta. Es decir, el agente solo te dice que ha terminado y esta por ver, mientra el cierre de alerta es la prueba de que está corregido.

3. **¿Qué parte del Lab 5 no ha hecho el asistente por sí solo en el Lab 8?**

El asistente no ha relizado la decisión del plan a seguir, ni tampoco el push ni PR del código al repositorio, pero si hecho el analisis y la corrección del código.

4. **¿Ha sido más rápido con el asistente? ¿En qué fases sí y en cuáles no?**

El asistente no ha sido necesariamente más rápido, en este caso más lento debido a que no tenia bien lo de la "integración con el terminal". En general, el análisis lo ha realizado de forma más exahustiva y precisa de lo que yo sería capaz, denado me muchas más opciones de que hacer, la corrección ha sido más rápida y la verificación tambien.