from app import db


class PlotUseType(db.Model):
    __tablename__ = 'plot_use_types'
    id_use_type_code = db.Column(db.Integer, primary_key=True)
    use_type = db.Column(db.String(128))
    plots = db.relationship('Plot', backref='plot_use_type')
