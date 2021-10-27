# The Redis Queue API

El challenge consta de implementar una cola de mensajes utilizando un Redis y además implementar una API que nos permita abstraernos.  
Se puede implementar con el lenguaje de programación que prefieras, frameworks y librerias que creas necesarios pero si es importante usar [Docker](https://www.docker.com/) para que sea reproducible facilmente y podamos probarlo.  
Esta **API** deberá estar conformada por 3 métodos (endpoints) que deben cumplir con el siguiente contrato:


### PUSH:
Metodo: `POST`   
Path: `/api/queue/push`  
Body: `<msg>` . 
Respuesta: `201` en caso de éxito y en caso de error un status code correspondiente al tipo de error . 
Body Respuesta:

    {
      ‘status’: ‘ok’,
    }

### POP:
Metodo: `POST`  
Path: `/api/queue/pop`  
Respuesta: `200` en caso de éxito y en caso de error un status code correspondiente al tipo de error  
Body Respuesta:

    {
      ‘status’: ‘ok’,
      ‘message’: <msg>
    }
    
### Count:
Metodo: `GET`  
Path: `/api/queue/count`  
Respuesta: `200` en caso de éxito y en caso de error un status code correspondiente al tipo de error  
Body Respuesta:

    {
      ‘status’: ‘ok’,
      ‘count’: <count>,
    }
    
    
Bonus, son opcionales pero se valoran mucho:
- Hacer tests que verifiquen el funcionamiento.
- Agregar funcionalidad a la api y cola. (Ej: autenticación de la api, logs, pop y push en batch, métricas, lo que se te ocurra)
- Endpoint de estado de salud de Redis.
- Documentación de cómo se implementó, si hay credenciales, cómo ejecutarlo, detalle de mejoras implementadas.

Cuanto más fácil sea reproducir el challenge, mejor :)
