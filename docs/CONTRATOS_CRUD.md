# Contratos de los CRUD

Esta guia describe las solicitudes y respuestas del backend antes de agregar autenticacion. Los identificadores de empresa delimitan consultas, pero todavia no sustituyen permisos ni verifican la identidad de quien consulta.

## Reglas comunes

- Crear devuelve 201; consultar y editar devuelven 200. Retirar una asignacion devuelve 204 sin cuerpo.
- Un registro inexistente o ajeno a la empresa indicada devuelve 404. Un duplicado devuelve 409. Los datos invalidos devuelven 422.
- Las listas paginadas devuelven total, pagina_actual, limite, total_paginas y data. El limite permitido es de 1 a 100.
- PATCH recibe solo los campos que se quieren cambiar. No acepta un objeto vacio ni campos desconocidos.
- Desactivar conserva el registro. Las asignaciones que tienen DELETE se retiran sin borrar el producto maestro.
- Un valor nulo solo se admite en campos opcionales que permiten limpiar su valor, como descripcion, telefono, capacidad o precio_especial.

## Disponibilidad por sucursal

Un producto maestro puede asignarse a varios locales de su empresa. La pareja producto-sucursal no se repite. El precio especial es opcional y no puede ser negativo. Retirar una asignacion no borra el producto ni las asignaciones de otros locales.

Ejemplo de creacion:

```json
{
  "id_producto": 1,
  "id_sucursal": 1,
  "disponible": true,
  "precio_especial": "60.00"
}
```

Enviar a POST /disponibilidad-productos/?id_empresa=1. Para volver al precio maestro, enviar PATCH con {"precio_especial": null}.

## Operaciones por modulo

### POST /empresas/

Crear Empresa

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Nueva_Empresa"}`

- 201: Successful Response; `{"$ref": "#/components/schemas/NuevaEmpresaRespuesta"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /empresas/

Ver Empresas

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| pagina_actual | query | No | {"type": "integer", "minimum": 1, "default": 1, "title": "Pagina Actual"} |
| limite | query | No | {"type": "integer", "maximum": 100, "minimum": 1, "default": 10, "title": "Limite"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPaginada_NuevaEmpresaRespuesta_"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /empresas/{id}

Ver Empresa

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/NuevaEmpresaRespuesta"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### PATCH /empresas/{id}

Editar Empresa

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Editar_Empresa"}`

- 200: Successful Response; `{"$ref": "#/components/schemas/NuevaEmpresaRespuesta"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /empresas/{id}/desactivar

Desactivar Empresa

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/NuevaEmpresaRespuesta"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /categorias/

Crear Categoria

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Nueva_Categoria"}`

- 201: Successful Response; `{"$ref": "#/components/schemas/NuevaCategoriaRespuesta"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /categorias/

Ver Categorias

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |
| pagina_actual | query | No | {"type": "integer", "minimum": 1, "default": 1, "title": "Pagina Actual"} |
| limite | query | No | {"type": "integer", "maximum": 100, "minimum": 1, "default": 10, "title": "Limite"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPaginada_NuevaCategoriaRespuesta_"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /categorias/{id}

Ver Categoria

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/NuevaCategoriaRespuesta"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### PATCH /categorias/{id}

Editar Categoria

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Editar_Categoria"}`

- 200: Successful Response; `{"$ref": "#/components/schemas/NuevaCategoriaRespuesta"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /categorias/{id}/desactivar

Desactivar Categoria

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/NuevaCategoriaRespuesta"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /productos/

Crear Producto

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Nuevo_Producto"}`

- 201: Successful Response; `{"$ref": "#/components/schemas/NuevoProductoRespuesta"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /productos/

Ver Productos

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |
| pagina_actual | query | No | {"type": "integer", "minimum": 1, "default": 1, "title": "Pagina Actual"} |
| limite | query | No | {"type": "integer", "maximum": 100, "minimum": 1, "default": 10, "title": "Limite"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPaginada_NuevoProductoRespuesta_"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /productos/{id}

Ver Producto

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/NuevoProductoRespuesta"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### PATCH /productos/{id}

Editar Producto

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Editar_Producto"}`

- 200: Successful Response; `{"$ref": "#/components/schemas/NuevoProductoRespuesta"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /productos/{id}/desactivar

Desactivar Producto

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/NuevoProductoRespuesta"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /usuarios/

Crear Usuario

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Nuevo_Usuario"}`

- 201: Successful Response; `{"$ref": "#/components/schemas/NuevoUsuarioRespuesta"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /usuarios/

Ver Usuarios

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| pagina_actual | query | No | {"type": "integer", "minimum": 1, "default": 1, "title": "Pagina Actual"} |
| limite | query | No | {"type": "integer", "maximum": 100, "minimum": 1, "default": 10, "title": "Limite"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPaginada_NuevoUsuarioRespuesta_"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /usuarios/{id}

Ver Usuario

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/NuevoUsuarioRespuesta"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### PATCH /usuarios/{id}

Editar Usuario

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Editar_Usuario"}`

- 200: Successful Response; `{"$ref": "#/components/schemas/NuevoUsuarioRespuesta"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /usuarios/{id}/desactivar

Desactivar Usuario

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/NuevoUsuarioRespuesta"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /sucursales/

Crear Sucursal

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Crear_Sucursal"}`

- 201: Successful Response; `{"$ref": "#/components/schemas/RespuestaSucursalCreada"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /sucursales/

Ver Sucursales

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |
| pagina_actual | query | No | {"type": "integer", "minimum": 1, "default": 1, "title": "Pagina Actual"} |
| limite | query | No | {"type": "integer", "maximum": 100, "minimum": 1, "default": 10, "title": "Limite"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPaginada_RespuestaSucursalCreada_"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /sucursales/{id}

Ver Sucursal

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaSucursalCreada"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### PATCH /sucursales/{id}

Editar Sucursal

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Editar_Sucursal"}`

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaSucursalEditada"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /sucursales/{id}/desactivar

Desactivar Sucursal

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaSucursalEditada"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /vinculos-laborales/

Crear Vinculo Laboral

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Crear_Vinculo_Laboral"}`

- 201: Successful Response; `{"$ref": "#/components/schemas/RespuestaVinculoLaboral"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /vinculos-laborales/

Ver Vinculos Laborales

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |
| pagina_actual | query | No | {"type": "integer", "minimum": 1, "default": 1, "title": "Pagina Actual"} |
| limite | query | No | {"type": "integer", "maximum": 100, "minimum": 1, "default": 10, "title": "Limite"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPaginada_RespuestaVinculoLaboral_"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /vinculos-laborales/{id}

Ver Vinculo Laboral

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaVinculoLaboralDetalle"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /vinculos-laborales/{id}/sucursales

Asignar Sucursal

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Asignar_Sucursal"}`

- 201: Successful Response; `{"$ref": "#/components/schemas/RespuestaAsignacionSucursal"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /vinculos-laborales/{id}/sucursales

Ver Asignaciones Sucursales

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |
| pagina_actual | query | No | {"type": "integer", "minimum": 1, "default": 1, "title": "Pagina Actual"} |
| limite | query | No | {"type": "integer", "maximum": 100, "minimum": 1, "default": 10, "title": "Limite"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPaginada_RespuestaAsignacionSucursal_"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### DELETE /vinculos-laborales/{id}/sucursales/{id_sucursal}

Quitar Asignacion Sucursal

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_sucursal | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Sucursal"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 204: Successful Response
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /mesas/

Crear Mesa

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Crear_Mesa"}`

- 201: Successful Response; `{"$ref": "#/components/schemas/RespuestaMesa"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /mesas/

Ver Mesas

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_sucursal | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Sucursal"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |
| pagina_actual | query | No | {"type": "integer", "minimum": 1, "default": 1, "title": "Pagina Actual"} |
| limite | query | No | {"type": "integer", "maximum": 100, "minimum": 1, "default": 10, "title": "Limite"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPaginada_RespuestaMesa_"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /mesas/{id}

Ver Mesa

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_sucursal | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Sucursal"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaMesa"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### PATCH /mesas/{id}

Editar Mesa

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_sucursal | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Sucursal"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Editar_Mesa"}`

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaMesa"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /mesas/{id}/desactivar

Desactivar Mesa

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_sucursal | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Sucursal"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaMesa"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /configuracion-impuestos/

Crear Configuracion Impuestos

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Crear_Configuracion_Impuestos"}`

- 201: Successful Response; `{"$ref": "#/components/schemas/RespuestaConfiguracionImpuestos"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /configuracion-impuestos/

Ver Configuraciones Impuestos

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |
| pagina_actual | query | No | {"type": "integer", "minimum": 1, "default": 1, "title": "Pagina Actual"} |
| limite | query | No | {"type": "integer", "maximum": 100, "minimum": 1, "default": 10, "title": "Limite"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPaginada_RespuestaConfiguracionImpuestos_"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /configuracion-impuestos/{id}

Ver Configuracion Impuestos

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaConfiguracionImpuestos"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### PATCH /configuracion-impuestos/{id}

Editar Configuracion Impuestos

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Editar_Configuracion_Impuestos"}`

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaConfiguracionImpuestos"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /configuracion-impuestos/{id}/desactivar

Desactivar Configuracion Impuestos

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaConfiguracionImpuestos"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /descuentos/

Crear Descuento

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Crear_Descuento"}`

- 201: Successful Response; `{"$ref": "#/components/schemas/RespuestaDescuento"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /descuentos/

Ver Descuentos

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |
| pagina_actual | query | No | {"type": "integer", "minimum": 1, "default": 1, "title": "Pagina Actual"} |
| limite | query | No | {"type": "integer", "maximum": 100, "minimum": 1, "default": 10, "title": "Limite"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPaginada_RespuestaDescuento_"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /descuentos/{id}

Ver Descuento

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaDescuento"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### PATCH /descuentos/{id}

Editar Descuento

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Editar_Descuento"}`

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaDescuento"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /descuentos/{id}/desactivar

Desactivar Descuento

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaDescuento"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /categorias-gastos/

Crear Categoria Gasto

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Crear_Categoria_Gasto"}`

- 201: Successful Response; `{"$ref": "#/components/schemas/RespuestaCategoriaGasto"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /categorias-gastos/

Ver Categorias Gastos

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |
| pagina_actual | query | No | {"type": "integer", "minimum": 1, "default": 1, "title": "Pagina Actual"} |
| limite | query | No | {"type": "integer", "maximum": 100, "minimum": 1, "default": 10, "title": "Limite"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPaginada_RespuestaCategoriaGasto_"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /categorias-gastos/{id}

Ver Categoria Gasto

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaCategoriaGasto"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### PATCH /categorias-gastos/{id}

Editar Categoria Gasto

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Editar_Categoria_Gasto"}`

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaCategoriaGasto"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /categorias-gastos/{id}/desactivar

Desactivar Categoria Gasto

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaCategoriaGasto"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /tipos-servicio/

Ver Tipos Servicio

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| pagina_actual | query | No | {"type": "integer", "minimum": 1, "default": 1, "title": "Pagina Actual"} |
| limite | query | No | {"type": "integer", "maximum": 100, "minimum": 1, "default": 10, "title": "Limite"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPaginada_RespuestaTipoServicio_"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /tipos-servicio/{id}

Ver Tipo Servicio

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaTipoServicio"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /metodos-pago/

Ver Metodos Pago

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| pagina_actual | query | No | {"type": "integer", "minimum": 1, "default": 1, "title": "Pagina Actual"} |
| limite | query | No | {"type": "integer", "maximum": 100, "minimum": 1, "default": 10, "title": "Limite"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPaginada_RespuestaMetodoPago_"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /metodos-pago/{id}

Ver Metodo Pago

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaMetodoPago"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /servicios-sucursales/

Crear Servicio Sucursal

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Crear_Servicio_Sucursal"}`

- 201: Successful Response; `{"$ref": "#/components/schemas/RespuestaServicioSucursal"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /servicios-sucursales/

Ver Servicios Sucursales

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_sucursal | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Sucursal"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |
| solo_habilitados | query | No | {"type": "boolean", "default": true, "title": "Solo Habilitados"} |
| pagina_actual | query | No | {"type": "integer", "minimum": 1, "default": 1, "title": "Pagina Actual"} |
| limite | query | No | {"type": "integer", "maximum": 100, "minimum": 1, "default": 10, "title": "Limite"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPaginada_RespuestaServicioSucursal_"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /servicios-sucursales/{id_sucursal}/{id_tipo_servicio}

Ver Servicio Sucursal

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_sucursal | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Sucursal"} |
| id_tipo_servicio | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Tipo Servicio"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaServicioSucursal"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### PATCH /servicios-sucursales/{id_sucursal}/{id_tipo_servicio}

Editar Servicio Sucursal

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_sucursal | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Sucursal"} |
| id_tipo_servicio | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Tipo Servicio"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Editar_Servicio_Sucursal"}`

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaServicioSucursal"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /servicios-sucursales/{id_sucursal}/{id_tipo_servicio}/desactivar

Desactivar Servicio Sucursal

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_sucursal | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Sucursal"} |
| id_tipo_servicio | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Tipo Servicio"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaServicioSucursal"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /pagos-sucursales/

Crear Pago Sucursal

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Crear_Pago_Sucursal"}`

- 201: Successful Response; `{"$ref": "#/components/schemas/RespuestaPagoSucursal"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /pagos-sucursales/

Ver Pagos Sucursales

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_sucursal | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Sucursal"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |
| solo_habilitados | query | No | {"type": "boolean", "default": true, "title": "Solo Habilitados"} |
| pagina_actual | query | No | {"type": "integer", "minimum": 1, "default": 1, "title": "Pagina Actual"} |
| limite | query | No | {"type": "integer", "maximum": 100, "minimum": 1, "default": 10, "title": "Limite"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPaginada_RespuestaPagoSucursal_"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /pagos-sucursales/{id_sucursal}/{id_metodo_pago}

Ver Pago Sucursal

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_sucursal | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Sucursal"} |
| id_metodo_pago | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Metodo Pago"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPagoSucursal"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### PATCH /pagos-sucursales/{id_sucursal}/{id_metodo_pago}

Editar Pago Sucursal

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_sucursal | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Sucursal"} |
| id_metodo_pago | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Metodo Pago"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Editar_Pago_Sucursal"}`

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPagoSucursal"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /pagos-sucursales/{id_sucursal}/{id_metodo_pago}/desactivar

Desactivar Pago Sucursal

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_sucursal | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Sucursal"} |
| id_metodo_pago | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Metodo Pago"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPagoSucursal"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### POST /disponibilidad-productos/

Crear Disponibilidad Producto

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Crear_Disponibilidad_Producto"}`

- 201: Successful Response; `{"$ref": "#/components/schemas/RespuestaDisponibilidadProducto"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /disponibilidad-productos/

Ver Disponibilidad Productos

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_sucursal | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Sucursal"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |
| pagina_actual | query | No | {"type": "integer", "minimum": 1, "default": 1, "title": "Pagina Actual"} |
| limite | query | No | {"type": "integer", "maximum": 100, "minimum": 1, "default": 10, "title": "Limite"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaPaginada_RespuestaDisponibilidadProducto_"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /disponibilidad-productos/{id_producto}/{id_sucursal}

Ver Disponibilidad Producto

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_producto | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Producto"} |
| id_sucursal | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Sucursal"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaDisponibilidadProducto"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### PATCH /disponibilidad-productos/{id_producto}/{id_sucursal}

Editar Disponibilidad Producto

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_producto | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Producto"} |
| id_sucursal | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Sucursal"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

Cuerpo: `{"$ref": "#/components/schemas/Revisar_Json_Editar_Disponibilidad_Producto"}`

- 200: Successful Response; `{"$ref": "#/components/schemas/RespuestaDisponibilidadProducto"}`
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### DELETE /disponibilidad-productos/{id_producto}/{id_sucursal}

Retirar Disponibilidad Producto

| Parametro | Donde va | Obligatorio | Tipo |
| --- | --- | --- | --- |
| id_producto | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Producto"} |
| id_sucursal | path | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Sucursal"} |
| id_empresa | query | Si | {"type": "integer", "exclusiveMinimum": 0, "title": "Id Empresa"} |

- 204: Successful Response
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

### GET /salud

Salud

- 200: Successful Response
- 404: Registro no encontrado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 409: Registro duplicado; `{"$ref": "#/components/schemas/RespuestaError"}`
- 422: Datos invalidos; `{"$ref": "#/components/schemas/RespuestaError"}`

## Campos de solicitudes y respuestas

Las referencias con el mismo nombre apuntan a los contratos que se detallan a continuacion. anyOf indica las alternativas admitidas; null permite enviar un valor nulo.

### NuevaCategoriaRespuesta

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id | Si | `{"type": "integer"}` |
| id_empresa | Si | `{"type": "integer"}` |
| nombre | Si | `{"type": "string"}` |
| orden_presentacion | Si | `{"type": "integer"}` |
| activo | Si | `{"type": "boolean"}` |

### NuevaEmpresaRespuesta

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| nombre | Si | `{"type": "string", "maxLength": 45, "minLength": 4}` |
| tipo_negocio | Si | `{"type": "string", "maxLength": 35, "minLength": 1}` |
| codigo_pais | Si | `{"type": "string", "maxLength": 5, "minLength": 2}` |
| zona_horaria | Si | `{"type": "string", "maxLength": 45, "minLength": 4}` |
| codigo_moneda | Si | `{"type": "string", "maxLength": 5, "minLength": 2}` |
| id | Si | `{"type": "integer"}` |
| estado | Si | `{"type": "string"}` |
| fecha_registro | Si | `{"type": "string", "format": "date-time"}` |

### NuevoProductoRespuesta

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id | Si | `{"type": "integer"}` |
| id_empresa | Si | `{"type": "integer"}` |
| id_categoria | Si | `{"anyOf": [{"type": "integer"}, {"type": "null"}]}` |
| nombre | Si | `{"type": "string"}` |
| descripcion | Si | `{"anyOf": [{"type": "string"}, {"type": "null"}]}` |
| precio | Si | `{"type": "string"}` |
| ruta_imagen | Si | `{"anyOf": [{"type": "string"}, {"type": "null"}]}` |
| disponible | Si | `{"type": "boolean"}` |

### NuevoUsuarioRespuesta

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id | Si | `{"type": "integer"}` |
| correo | Si | `{"type": "string", "format": "email"}` |
| nombre | Si | `{"type": "string"}` |
| estado | Si | `{"type": "boolean"}` |
| fecha_registro | Si | `{"type": "string", "format": "date-time"}` |

### RespuestaAsignacionSucursal

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id | Si | `{"type": "integer"}` |
| id_vinculo_laboral | Si | `{"type": "integer"}` |
| id_sucursal | Si | `{"type": "integer"}` |

### RespuestaCategoriaGasto

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id | Si | `{"type": "integer"}` |
| id_empresa | Si | `{"type": "integer"}` |
| nombre | Si | `{"type": "string"}` |
| activo | Si | `{"type": "boolean"}` |

### RespuestaConfiguracionImpuestos

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id | Si | `{"type": "integer"}` |
| id_empresa | Si | `{"type": "integer"}` |
| nombre | Si | `{"anyOf": [{"type": "string"}, {"type": "null"}]}` |
| porcentaje | Si | `{"type": "string"}` |
| precios_incluyen_impuesto | Si | `{"type": "boolean"}` |
| activo | Si | `{"type": "boolean"}` |

### RespuestaDescuento

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id | Si | `{"type": "integer"}` |
| id_empresa | Si | `{"type": "integer"}` |
| nombre | Si | `{"type": "string"}` |
| tipo_descuento | Si | `{"type": "string", "enum": ["Porcentaje", "CantidadFija"]}` |
| valor | Si | `{"type": "string"}` |
| activo | Si | `{"type": "boolean"}` |

### RespuestaDisponibilidadProducto

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id_producto | Si | `{"type": "integer"}` |
| id_sucursal | Si | `{"type": "integer"}` |
| disponible | Si | `{"type": "boolean"}` |
| precio_especial | Si | `{"anyOf": [{"type": "string"}, {"type": "null"}]}` |

### RespuestaError

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| detail | Si | `{"type": "string"}` |
| errores | No | `{"anyOf": [{"items": {"additionalProperties": true, "type": "object"}, "type": "array"}, {"type": "null"}]}` |

### RespuestaMesa

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id | Si | `{"type": "integer"}` |
| id_sucursal | Si | `{"type": "integer"}` |
| nombre | Si | `{"type": "string"}` |
| capacidad | Si | `{"anyOf": [{"type": "integer"}, {"type": "null"}]}` |
| activo | Si | `{"type": "boolean"}` |

### RespuestaMetodoPago

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id | Si | `{"type": "integer"}` |
| clave_concepto | Si | `{"type": "string"}` |
| nombre_visible | Si | `{"type": "string"}` |
| activo | Si | `{"type": "boolean"}` |

### RespuestaPaginada_NuevaCategoriaRespuesta_

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| total | Si | `{"type": "integer"}` |
| pagina_actual | Si | `{"type": "integer"}` |
| limite | Si | `{"type": "integer"}` |
| total_paginas | Si | `{"type": "integer"}` |
| data | Si | `{"items": {"$ref": "#/components/schemas/NuevaCategoriaRespuesta"}, "type": "array"}` |

### RespuestaPaginada_NuevaEmpresaRespuesta_

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| total | Si | `{"type": "integer"}` |
| pagina_actual | Si | `{"type": "integer"}` |
| limite | Si | `{"type": "integer"}` |
| total_paginas | Si | `{"type": "integer"}` |
| data | Si | `{"items": {"$ref": "#/components/schemas/NuevaEmpresaRespuesta"}, "type": "array"}` |

### RespuestaPaginada_NuevoProductoRespuesta_

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| total | Si | `{"type": "integer"}` |
| pagina_actual | Si | `{"type": "integer"}` |
| limite | Si | `{"type": "integer"}` |
| total_paginas | Si | `{"type": "integer"}` |
| data | Si | `{"items": {"$ref": "#/components/schemas/NuevoProductoRespuesta"}, "type": "array"}` |

### RespuestaPaginada_NuevoUsuarioRespuesta_

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| total | Si | `{"type": "integer"}` |
| pagina_actual | Si | `{"type": "integer"}` |
| limite | Si | `{"type": "integer"}` |
| total_paginas | Si | `{"type": "integer"}` |
| data | Si | `{"items": {"$ref": "#/components/schemas/NuevoUsuarioRespuesta"}, "type": "array"}` |

### RespuestaPaginada_RespuestaAsignacionSucursal_

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| total | Si | `{"type": "integer"}` |
| pagina_actual | Si | `{"type": "integer"}` |
| limite | Si | `{"type": "integer"}` |
| total_paginas | Si | `{"type": "integer"}` |
| data | Si | `{"items": {"$ref": "#/components/schemas/RespuestaAsignacionSucursal"}, "type": "array"}` |

### RespuestaPaginada_RespuestaCategoriaGasto_

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| total | Si | `{"type": "integer"}` |
| pagina_actual | Si | `{"type": "integer"}` |
| limite | Si | `{"type": "integer"}` |
| total_paginas | Si | `{"type": "integer"}` |
| data | Si | `{"items": {"$ref": "#/components/schemas/RespuestaCategoriaGasto"}, "type": "array"}` |

### RespuestaPaginada_RespuestaConfiguracionImpuestos_

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| total | Si | `{"type": "integer"}` |
| pagina_actual | Si | `{"type": "integer"}` |
| limite | Si | `{"type": "integer"}` |
| total_paginas | Si | `{"type": "integer"}` |
| data | Si | `{"items": {"$ref": "#/components/schemas/RespuestaConfiguracionImpuestos"}, "type": "array"}` |

### RespuestaPaginada_RespuestaDescuento_

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| total | Si | `{"type": "integer"}` |
| pagina_actual | Si | `{"type": "integer"}` |
| limite | Si | `{"type": "integer"}` |
| total_paginas | Si | `{"type": "integer"}` |
| data | Si | `{"items": {"$ref": "#/components/schemas/RespuestaDescuento"}, "type": "array"}` |

### RespuestaPaginada_RespuestaDisponibilidadProducto_

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| total | Si | `{"type": "integer"}` |
| pagina_actual | Si | `{"type": "integer"}` |
| limite | Si | `{"type": "integer"}` |
| total_paginas | Si | `{"type": "integer"}` |
| data | Si | `{"items": {"$ref": "#/components/schemas/RespuestaDisponibilidadProducto"}, "type": "array"}` |

### RespuestaPaginada_RespuestaMesa_

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| total | Si | `{"type": "integer"}` |
| pagina_actual | Si | `{"type": "integer"}` |
| limite | Si | `{"type": "integer"}` |
| total_paginas | Si | `{"type": "integer"}` |
| data | Si | `{"items": {"$ref": "#/components/schemas/RespuestaMesa"}, "type": "array"}` |

### RespuestaPaginada_RespuestaMetodoPago_

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| total | Si | `{"type": "integer"}` |
| pagina_actual | Si | `{"type": "integer"}` |
| limite | Si | `{"type": "integer"}` |
| total_paginas | Si | `{"type": "integer"}` |
| data | Si | `{"items": {"$ref": "#/components/schemas/RespuestaMetodoPago"}, "type": "array"}` |

### RespuestaPaginada_RespuestaPagoSucursal_

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| total | Si | `{"type": "integer"}` |
| pagina_actual | Si | `{"type": "integer"}` |
| limite | Si | `{"type": "integer"}` |
| total_paginas | Si | `{"type": "integer"}` |
| data | Si | `{"items": {"$ref": "#/components/schemas/RespuestaPagoSucursal"}, "type": "array"}` |

### RespuestaPaginada_RespuestaServicioSucursal_

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| total | Si | `{"type": "integer"}` |
| pagina_actual | Si | `{"type": "integer"}` |
| limite | Si | `{"type": "integer"}` |
| total_paginas | Si | `{"type": "integer"}` |
| data | Si | `{"items": {"$ref": "#/components/schemas/RespuestaServicioSucursal"}, "type": "array"}` |

### RespuestaPaginada_RespuestaSucursalCreada_

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| total | Si | `{"type": "integer"}` |
| pagina_actual | Si | `{"type": "integer"}` |
| limite | Si | `{"type": "integer"}` |
| total_paginas | Si | `{"type": "integer"}` |
| data | Si | `{"items": {"$ref": "#/components/schemas/RespuestaSucursalCreada"}, "type": "array"}` |

### RespuestaPaginada_RespuestaTipoServicio_

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| total | Si | `{"type": "integer"}` |
| pagina_actual | Si | `{"type": "integer"}` |
| limite | Si | `{"type": "integer"}` |
| total_paginas | Si | `{"type": "integer"}` |
| data | Si | `{"items": {"$ref": "#/components/schemas/RespuestaTipoServicio"}, "type": "array"}` |

### RespuestaPaginada_RespuestaVinculoLaboral_

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| total | Si | `{"type": "integer"}` |
| pagina_actual | Si | `{"type": "integer"}` |
| limite | Si | `{"type": "integer"}` |
| total_paginas | Si | `{"type": "integer"}` |
| data | Si | `{"items": {"$ref": "#/components/schemas/RespuestaVinculoLaboral"}, "type": "array"}` |

### RespuestaPagoSucursal

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id_sucursal | Si | `{"type": "integer"}` |
| id_metodo_pago | Si | `{"type": "integer"}` |
| habilitado | Si | `{"type": "boolean"}` |

### RespuestaServicioSucursal

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id_sucursal | Si | `{"type": "integer"}` |
| id_tipo_servicio | Si | `{"type": "integer"}` |
| habilitado | Si | `{"type": "boolean"}` |
| mesas_habilitadas | Si | `{"type": "boolean"}` |
| reservas_habilitadas | Si | `{"type": "boolean"}` |

### RespuestaSucursalCreada

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id_empresa | Si | `{"type": "integer", "exclusiveMinimum": 0.0}` |
| nombre | Si | `{"type": "string", "maxLength": 100, "minLength": 2}` |
| direccion | Si | `{"type": "string", "maxLength": 255, "minLength": 5}` |
| telefono | No | `{"anyOf": [{"type": "string", "maxLength": 20, "minLength": 8}, {"type": "null"}]}` |
| es_principal | No | `{"type": "boolean", "default": false}` |
| id | Si | `{"type": "integer"}` |
| activo | Si | `{"type": "boolean"}` |

### RespuestaSucursalEditada

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id_empresa | Si | `{"type": "integer", "exclusiveMinimum": 0.0}` |
| nombre | Si | `{"type": "string", "maxLength": 100, "minLength": 2}` |
| direccion | Si | `{"type": "string", "maxLength": 255, "minLength": 5}` |
| telefono | No | `{"anyOf": [{"type": "string", "maxLength": 20, "minLength": 8}, {"type": "null"}]}` |
| es_principal | No | `{"type": "boolean", "default": false}` |
| id | Si | `{"type": "integer"}` |
| activo | Si | `{"type": "boolean"}` |

### RespuestaTipoServicio

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id | Si | `{"type": "integer"}` |
| clave_concepto | Si | `{"type": "string"}` |
| nombre_visible | Si | `{"type": "string"}` |
| activo | Si | `{"type": "boolean"}` |

### RespuestaVinculoLaboral

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id | Si | `{"type": "integer"}` |
| id_usuario | Si | `{"type": "integer"}` |
| id_empresa | Si | `{"type": "integer"}` |
| rol | Si | `{"type": "string"}` |

### RespuestaVinculoLaboralDetalle

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id | Si | `{"type": "integer"}` |
| id_usuario | Si | `{"type": "integer"}` |
| id_empresa | Si | `{"type": "integer"}` |
| rol | Si | `{"type": "string"}` |
| asignaciones_sucursales | No | `{"items": {"$ref": "#/components/schemas/RespuestaAsignacionSucursal"}, "type": "array"}` |

### Revisar_Json_Asignar_Sucursal

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id_sucursal | Si | `{"type": "integer", "exclusiveMinimum": 0.0}` |

### Revisar_Json_Crear_Categoria_Gasto

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id_empresa | Si | `{"type": "integer", "exclusiveMinimum": 0.0}` |
| nombre | Si | `{"type": "string", "maxLength": 100, "minLength": 1}` |

### Revisar_Json_Crear_Configuracion_Impuestos

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id_empresa | Si | `{"type": "integer", "exclusiveMinimum": 0.0}` |
| nombre | No | `{"anyOf": [{"type": "string", "maxLength": 80, "minLength": 1}, {"type": "null"}]}` |
| porcentaje | Si | `{"anyOf": [{"type": "number", "maximum": 100.0, "minimum": 0.0}, {"type": "string"}]}` |
| precios_incluyen_impuesto | Si | `{"type": "boolean"}` |

### Revisar_Json_Crear_Descuento

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id_empresa | Si | `{"type": "integer", "exclusiveMinimum": 0.0}` |
| nombre | Si | `{"type": "string", "maxLength": 100, "minLength": 1}` |
| tipo_descuento | Si | `{"type": "string", "enum": ["Porcentaje", "CantidadFija"]}` |
| valor | Si | `{"anyOf": [{"type": "number", "minimum": 0.0}, {"type": "string"}]}` |

### Revisar_Json_Crear_Disponibilidad_Producto

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id_producto | Si | `{"type": "integer", "exclusiveMinimum": 0.0}` |
| id_sucursal | Si | `{"type": "integer", "exclusiveMinimum": 0.0}` |
| disponible | No | `{"type": "boolean", "default": true}` |
| precio_especial | No | `{"anyOf": [{"type": "number", "minimum": 0.0}, {"type": "string"}, {"type": "null"}]}` |

### Revisar_Json_Crear_Mesa

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id_sucursal | Si | `{"type": "integer", "exclusiveMinimum": 0.0}` |
| nombre | Si | `{"type": "string", "maxLength": 60, "minLength": 1}` |
| capacidad | No | `{"anyOf": [{"type": "integer", "exclusiveMinimum": 0.0}, {"type": "null"}]}` |

### Revisar_Json_Crear_Pago_Sucursal

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id_sucursal | Si | `{"type": "integer", "exclusiveMinimum": 0.0}` |
| id_metodo_pago | Si | `{"type": "integer", "exclusiveMinimum": 0.0}` |
| habilitado | No | `{"type": "boolean", "default": false}` |

### Revisar_Json_Crear_Servicio_Sucursal

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id_sucursal | Si | `{"type": "integer", "exclusiveMinimum": 0.0}` |
| id_tipo_servicio | Si | `{"type": "integer", "exclusiveMinimum": 0.0}` |
| habilitado | No | `{"type": "boolean", "default": false}` |
| mesas_habilitadas | No | `{"type": "boolean", "default": false}` |
| reservas_habilitadas | No | `{"type": "boolean", "default": false}` |

### Revisar_Json_Crear_Sucursal

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id_empresa | Si | `{"type": "integer", "exclusiveMinimum": 0.0}` |
| nombre | Si | `{"type": "string", "maxLength": 100, "minLength": 2}` |
| direccion | Si | `{"type": "string", "maxLength": 255, "minLength": 5}` |
| telefono | No | `{"anyOf": [{"type": "string", "maxLength": 20, "minLength": 8}, {"type": "null"}]}` |
| es_principal | No | `{"type": "boolean", "default": false}` |

### Revisar_Json_Crear_Vinculo_Laboral

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id_usuario | Si | `{"type": "integer", "exclusiveMinimum": 0.0}` |
| id_empresa | Si | `{"type": "integer", "exclusiveMinimum": 0.0}` |
| rol | Si | `{"type": "string", "maxLength": 40, "minLength": 2}` |

### Revisar_Json_Editar_Categoria

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| activo | No | `{"anyOf": [{"type": "boolean"}, {"type": "null"}]}` |
| nombre | No | `{"anyOf": [{"type": "string", "maxLength": 60, "minLength": 1}, {"type": "null"}]}` |
| orden_presentacion | No | `{"anyOf": [{"type": "integer", "minimum": 0.0}, {"type": "null"}]}` |

### Revisar_Json_Editar_Categoria_Gasto

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| nombre | No | `{"anyOf": [{"type": "string", "maxLength": 100, "minLength": 1}, {"type": "null"}]}` |
| activo | No | `{"anyOf": [{"type": "boolean"}, {"type": "null"}]}` |

### Revisar_Json_Editar_Configuracion_Impuestos

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| nombre | No | `{"anyOf": [{"type": "string", "maxLength": 80, "minLength": 1}, {"type": "null"}]}` |
| porcentaje | No | `{"anyOf": [{"type": "number", "maximum": 100.0, "minimum": 0.0}, {"type": "string"}, {"type": "null"}]}` |
| precios_incluyen_impuesto | No | `{"anyOf": [{"type": "boolean"}, {"type": "null"}]}` |
| activo | No | `{"anyOf": [{"type": "boolean"}, {"type": "null"}]}` |

### Revisar_Json_Editar_Descuento

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| nombre | No | `{"anyOf": [{"type": "string", "maxLength": 100, "minLength": 1}, {"type": "null"}]}` |
| tipo_descuento | No | `{"anyOf": [{"type": "string", "enum": ["Porcentaje", "CantidadFija"]}, {"type": "null"}]}` |
| valor | No | `{"anyOf": [{"type": "number", "minimum": 0.0}, {"type": "string"}, {"type": "null"}]}` |
| activo | No | `{"anyOf": [{"type": "boolean"}, {"type": "null"}]}` |

### Revisar_Json_Editar_Disponibilidad_Producto

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| disponible | No | `{"anyOf": [{"type": "boolean"}, {"type": "null"}]}` |
| precio_especial | No | `{"anyOf": [{"type": "number", "minimum": 0.0}, {"type": "string"}, {"type": "null"}]}` |

### Revisar_Json_Editar_Empresa

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| nombre | No | `{"anyOf": [{"type": "string", "maxLength": 45, "minLength": 4}, {"type": "null"}]}` |
| tipo_negocio | No | `{"anyOf": [{"type": "string", "maxLength": 35, "minLength": 1}, {"type": "null"}]}` |
| codigo_pais | No | `{"anyOf": [{"type": "string", "maxLength": 5, "minLength": 2}, {"type": "null"}]}` |
| zona_horaria | No | `{"anyOf": [{"type": "string", "maxLength": 45, "minLength": 4}, {"type": "null"}]}` |
| codigo_moneda | No | `{"anyOf": [{"type": "string", "maxLength": 5, "minLength": 2}, {"type": "null"}]}` |

### Revisar_Json_Editar_Mesa

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| activo | No | `{"anyOf": [{"type": "boolean"}, {"type": "null"}]}` |
| nombre | No | `{"anyOf": [{"type": "string", "maxLength": 60, "minLength": 1}, {"type": "null"}]}` |
| capacidad | No | `{"anyOf": [{"type": "integer", "exclusiveMinimum": 0.0}, {"type": "null"}]}` |

### Revisar_Json_Editar_Pago_Sucursal

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| habilitado | No | `{"anyOf": [{"type": "boolean"}, {"type": "null"}]}` |

### Revisar_Json_Editar_Producto

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| disponible | No | `{"anyOf": [{"type": "boolean"}, {"type": "null"}]}` |
| id_categoria | No | `{"anyOf": [{"type": "integer", "exclusiveMinimum": 0.0}, {"type": "null"}]}` |
| nombre | No | `{"anyOf": [{"type": "string", "maxLength": 100, "minLength": 1}, {"type": "null"}]}` |
| descripcion | No | `{"anyOf": [{"type": "string"}, {"type": "null"}]}` |
| precio | No | `{"anyOf": [{"type": "number", "minimum": 0.0}, {"type": "string"}, {"type": "null"}]}` |

### Revisar_Json_Editar_Servicio_Sucursal

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| habilitado | No | `{"anyOf": [{"type": "boolean"}, {"type": "null"}]}` |
| mesas_habilitadas | No | `{"anyOf": [{"type": "boolean"}, {"type": "null"}]}` |
| reservas_habilitadas | No | `{"anyOf": [{"type": "boolean"}, {"type": "null"}]}` |

### Revisar_Json_Editar_Sucursal

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| activo | No | `{"anyOf": [{"type": "boolean"}, {"type": "null"}]}` |
| nombre | No | `{"anyOf": [{"type": "string", "maxLength": 100, "minLength": 2}, {"type": "null"}]}` |
| direccion | No | `{"anyOf": [{"type": "string", "maxLength": 255, "minLength": 5}, {"type": "null"}]}` |
| telefono | No | `{"anyOf": [{"type": "string", "maxLength": 20, "minLength": 8}, {"type": "null"}]}` |
| es_principal | No | `{"anyOf": [{"type": "boolean"}, {"type": "null"}]}` |

### Revisar_Json_Editar_Usuario

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| estado | No | `{"anyOf": [{"type": "boolean"}, {"type": "null"}]}` |
| correo | No | `{"anyOf": [{"type": "string", "format": "email"}, {"type": "null"}]}` |
| nombre | No | `{"anyOf": [{"type": "string", "maxLength": 100, "minLength": 1}, {"type": "null"}]}` |

### Revisar_Json_Nueva_Categoria

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id_empresa | Si | `{"type": "integer", "exclusiveMinimum": 0.0}` |
| nombre | Si | `{"type": "string", "maxLength": 60, "minLength": 1}` |
| orden_presentacion | No | `{"type": "integer", "minimum": 0.0, "default": 1}` |

### Revisar_Json_Nueva_Empresa

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| nombre | Si | `{"type": "string", "maxLength": 45, "minLength": 4}` |
| tipo_negocio | Si | `{"type": "string", "maxLength": 35, "minLength": 1}` |
| codigo_pais | Si | `{"type": "string", "maxLength": 5, "minLength": 2}` |
| zona_horaria | Si | `{"type": "string", "maxLength": 45, "minLength": 4}` |
| codigo_moneda | Si | `{"type": "string", "maxLength": 5, "minLength": 2}` |

### Revisar_Json_Nuevo_Producto

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| id_empresa | Si | `{"type": "integer", "exclusiveMinimum": 0.0}` |
| id_categoria | No | `{"anyOf": [{"type": "integer", "exclusiveMinimum": 0.0}, {"type": "null"}]}` |
| nombre | Si | `{"type": "string", "maxLength": 100, "minLength": 1}` |
| descripcion | No | `{"anyOf": [{"type": "string"}, {"type": "null"}]}` |
| precio | Si | `{"anyOf": [{"type": "number", "minimum": 0.0}, {"type": "string"}]}` |

### Revisar_Json_Nuevo_Usuario

| Campo | Obligatorio | Definicion |
| --- | --- | --- |
| correo | Si | `{"type": "string", "format": "email"}` |
| nombre | Si | `{"type": "string", "maxLength": 100, "minLength": 1}` |

## Cambios para quien conecte el frontend

- Productos usa ahora la misma envoltura paginada de las otras listas.
- Las categorias desactivadas se conservan en las consultas.
- Mesas y asignaciones laborales requieren indicar la empresa para evitar consultas cruzadas.
- Los campos desconocidos, PATCH vacios y valores nulos no permitidos devuelven 422.
- Los mensajes de error no incluyen consultas SQL ni credenciales.

La documentacion interactiva de /docs permite enviar ejemplos y muestra los contratos vigentes. Esta etapa no incluye login, roles, calculo de pedidos ni cobros.
