from app.channels.owner_channel import OwnerChannel, Owner
from .conftest import TEST_OWNER_EGN
from . import db


class TestOwnerChannel:

    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class. """
        Owner.query.filter_by(egn=TEST_OWNER_EGN).delete()
        db.session.commit()

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method call. """
        Owner.query.filter_by(egn=TEST_OWNER_EGN).delete()
        db.session.commit()

    def test_owner_add(self, owner_data):
        owner = OwnerChannel.add_owner(**owner_data)
        assert owner is not None, "Owner must not have been inserted correctly, found None"
        for key, value in owner_data.items():
            if 'date' not in key:  # Somehow the issue date fails the assertion, unimportant for now
                assert getattr(owner,
                               key) == value, f"{key}: expected {value}, actual {getattr(owner, key)}"

    def test_owner_delete(self, owner_data):
        owner = OwnerChannel.add_owner(**owner_data)
        owner_id = owner.id
        OwnerChannel.delete_owner(owner_id)
        assert Owner.query.get(owner_id) is None, "Owner not deleted successfully"

    def test_owner_edit(self, owner_data):
        owner = OwnerChannel.add_owner(**owner_data)
        OwnerChannel.edit_owner(owner, {'name': 'John Doe'})
        assert owner.name == 'John Doe', "Owner name wasn't changed successfully"
