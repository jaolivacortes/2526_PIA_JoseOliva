import boto3
import re

rekognition = boto3.client('rekognition', region_name='us-east-1')
s3 = boto3.client('s3')

BUCKET = 'practica-rekognition-imagenes'

def es_matricula(texto):
    return 5 <= len(texto) <= 10 and re.search(r'[A-Za-z]', texto) and re.search(r'\d', texto)

# Listar imágenes en el bucket
response = s3.list_objects_v2(Bucket=BUCKET)
if 'Contents' not in response:
    print("No hay imágenes en el bucket")
    exit()

imagenes = [obj['Key'] for obj in response['Contents'] if obj['Key'].lower().endswith(('.jpg', '.png'))]
if not imagenes:
    print("No hay imágenes jpg/png en el bucket")
    exit()

for imagen in imagenes:
    print(f"\nProcesando {imagen}...")
    # Detectar coches
    response_labels = rekognition.detect_labels(Image={'S3Object': {'Bucket': BUCKET, 'Name': imagen}}, MaxLabels=10)
    coche_detectado = any(label['Name'].lower() in ['car', 'vehicle', 'automobile'] and label['Confidence'] > 90
                          for label in response_labels['Labels'])
    if not coche_detectado:
        print("No se detecta coche.")
        continue
    print("Coche detectado.")
    # Detectar matrículas
    response_text = rekognition.detect_text(Image={'S3Object': {'Bucket': BUCKET, 'Name': imagen}})
    matriculas = [text['DetectedText'] for text in response_text['TextDetections']
                  if text['Type'] == 'LINE' and text['Confidence'] > 90 and es_matricula(text['DetectedText'])]
    if matriculas:
        print("Matrículas detectadas:", ", ".join(matriculas))
    else:
        print("No se detectan matrículas.")
