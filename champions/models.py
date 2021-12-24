from django.db import models
import json
import os

DATA_DIR = "/datos/data_dragon/data/es_MX/champion"

class Champion(models.Model):
    """Campeon del juego.

    Esta clase guarda sus atributos basicos de identificacion,
    los detalles se guardan en un archivo JSON.
    """
    identifier = models.CharField(max_length=20)
    key = models.CharField(max_length=4)
    name = models.CharField(max_length=20)

    def __str__(self):
        """Devuelve la descripcion del objeto."""
        return self.name

    def get_data(self):
        """Devuelve los datos guardados en formato JSON del campeon."""
        filepath = DATA_DIR + "/" + self.identifier + ".json"
        rawdata = {}
        if os.path.isfile(filepath):
            with open(filepath, 'r') as f:
                rawdata = json.load(f)
        data = rawdata.get('data', {})
        return data.get(self.identifier, {})
