#!/usr/bin/python3
"""Unittest module for the BaseModel Class."""

from models import storage
from models.base_model import BaseModel
from models.engine.file_storage import FileStorage
from datetime import datetime
import json
import os
import re
import time
import unittest
import uuid


class TestBaseModel(unittest.TestCase):

    """Test Cases for the BaseModel class."""

    def setUp(self):
        """Sets up test methods."""
        pass

    def tearDown(self):
        """Tears down test methods."""
        self.resetStorage()
        pass

    def resetStorage(self):
        """Resets FileStorage data."""
        FileStorage._FileStorage__objects = {}
        if os.path.isfile(FileStorage._FileStorage__file_path):
            os.remove(FileStorage._FileStorage__file_path)

    def test_3_instantiation(self):
        """Tests instantiation of BaseModel class."""

        bm = BaseModel()
        self.assertEqual(str(type(bm)),
                                    "<class 'models.base_model.BaseModel'>")
        self.assertIsInstance(bm, BaseModel)
        self.assertTrue(issubclass(type(bm), BaseModel))

    def test_3_init_no_args(self):
        """Tests __init__ with no arguments."""
        self.resetStorage()
        with self.assertRaises(TypeError) as e1:
            BaseModel.__init__()
        msg = "__init__() missing 1 required positional argument: 'self'"
        self.assertEqual(str(e1.exception), msg)

    def test_3_init_many_args(self):
        """Tests __init__ with many arguments."""
        self.resetStorage()
        args = [i for i in range(1000)]
        bm = BaseModel(0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        bm = BaseModel(*args)

    def test_3_attributes(self):
        """Tests attributes value for instance of a BaseModel class."""

        attributes = storage.attributes()["BaseModel"]
        ol = BaseModel()
        for k, v in attributes.items():
            self.assertTrue(hasattr(ol, k))
            self.assertEqual(type(getattr(ol, k, None)), v)

    def test_3_datetime_created(self):
        """Tests if updated_at & created_at are current at creation."""
        date_now = datetime.now()
        bm = BaseModel()
        diff = bm.updated_at - bm.created_at
        self.assertTrue(abs(diff.total_seconds()) < 0.01)
        diff = bm.created_at - date_now
        self.assertTrue(abs(diff.total_seconds()) < 0.1)

    def test_3_id(self):
        """Tests for unique user ids."""

        la = [BaseModel().id for i in range(1000)]
        self.assertEqual(len(set(la)), len(la))

    def test_3_save(self):
        """Tests the public instance method save()."""

        bm = BaseModel()
        time.sleep(0.5)
        date_now = datetime.now()
        bm.save()
        diff = bm.updated_at - date_now
        self.assertTrue(abs(diff.total_seconds()) < 0.01)

    def test_3_str(self):
        """Tests for __str__ method."""
        bm = BaseModel()
        rex = re.compile(r"^\[(.*)\] \((.*)\) (.*)$")
        res = rex.match(str(bm))
        self.assertIsNotNone(res)
        self.assertEqual(res.group(1), "BaseModel")
        self.assertEqual(res.group(2), bm.id)
        s1 = res.group(3)
        s1 = re.sub(r"(datetime\.datetime\([^)]*\))", "'\\1'", s1)
        df = json.loads(s1.replace("'", '"'))
        d2 = bm.__dict__.copy()
        d2["created_at"] = repr(d2["created_at"])
        d2["updated_at"] = repr(d2["updated_at"])
        self.assertEqual(df, d2)

    def test_3_to_dict(self):
        """Tests the public instance method to_dict()."""

        bm = BaseModel()
        bm.name = "Maryam"
        bm.age = 25
        df = bm.to_dict()
        self.assertEqual(df["id"], bm.id)
        self.assertEqual(df["__class__"], type(bm).__name__)
        self.assertEqual(df["created_at"], bm.created_at.isoformat())
        self.assertEqual(df["updated_at"], bm.updated_at.isoformat())
        self.assertEqual(df["name"], bm.name)
        self.assertEqual(df["age"], bm.age)

    def test_3_to_dict_no_args(self):
        """Tests to_dict() with no arguments."""
        self.resetStorage()
        with self.assertRaises(TypeError) as e1:
            BaseModel.to_dict()
        msg = "to_dict() missing 1 required positional argument: 'self'"
        self.assertEqual(str(e1.exception), msg)

    def test_3_to_dict_excess_args(self):
        """Tests to_dict() with too many arguments."""
        self.resetStorage()
        with self.assertRaises(TypeError) as e1:
            BaseModel.to_dict(self, 98)
        msg = "to_dict() takes 1 positional argument but 2 were given"
        self.assertEqual(str(e1.exception), msg)

    def test_4_instantiation(self):
        """Tests instantiation with **kwargs."""

        my_model = BaseModel()
        my_model.name = "My First Model"
        my_model.my_number = 89
        my_model_json = my_model.to_dict()
        my_new_model = BaseModel(**my_model_json)
        self.assertEqual(my_new_model.to_dict(), my_model.to_dict())

    def test_4_instantiation_dict(self):
        """Tests instantiation with **kwargs from custom dict."""
        df = {"__class__": "BaseModel",
              "updated_at":
                    datetime(2050, 12, 30, 23, 59, 59, 123456).isoformat(),
              "created_at": datetime.now().isoformat(),
              "id": uuid.uuid4(),
              "var": "foobar",
              "int": 108,
              "float": 3.14}
        ol = BaseModel(**df)
        self.assertEqual(ol.to_dict(), df)

    def test_5_save(self):
        """Tests that storage.save() is called from save()."""
        self.resetStorage()
        bm = BaseModel()
        bm.save()
        key = "{}.{}".format(type(bm).__name__, bm.id)
        df = {key: bm.to_dict()}
        self.assertTrue(os.path.isfile(FileStorage._FileStorage__file_path))
        with open(FileStorage._FileStorage__file_path,
                  "r", encoding="utf-8") as f:
            self.assertEqual(len(f.read()), len(json.dumps(df)))
            f.seek(0)
            self.assertEqual(json.load(f), df)

    def test_5_save_no_args(self):
        """Tests save() with no arguments."""
        self.resetStorage()
        with self.assertRaises(TypeError) as e1:
            BaseModel.save()
        msg = "save() missing 1 required positional argument: 'self'"
        self.assertEqual(str(e1.exception), msg)

    def test_5_save_excess_args(self):
        """Tests save() with too many arguments."""
        self.resetStorage()
        with self.assertRaises(TypeError) as e1:
            BaseModel.save(self, 98)
        msg = "save() takes 1 positional argument but 2 were given"
        self.assertEqual(str(e1.exception), msg)


if __name__ == '__main__':
    unittest.main()
