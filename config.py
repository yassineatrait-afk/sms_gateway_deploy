class Config:
    # notez l'ajout de "+pymysql" et l'encodage du '@' dans le mot de passe (%40)
    SQLALCHEMY_DATABASE_URI = (
      "mysql+pymysql://sms_user:PASSWORD%40@localhost/sms_gateway"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

