from app import db


class AbstractChannel:

    @classmethod
    def add_objects(cls, objects):
        try:
            for obj in objects:
                db.session.add(obj)
            db.session.commit()
        except Exception as inst:
            print(inst)

    @classmethod
    def add_object(cls, obj):
        try:
            db.session.add(obj)
            db.session.commit()
        except Exception as inst:
            print(inst)
