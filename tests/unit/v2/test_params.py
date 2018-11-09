#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
import shutil, tempfile
from unittest import TestCase
from auror.v2.params import Params, Env, SparkExecutor, SparkDriver, ParamsJoin, SparkConfig


class ParamsTest(TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp() # Create a temporary directory
        key_vals = {"param_name_1": "value_1", "param_name_2": "value_2"}
        self.data_params = Params("name_teste_params", **key_vals)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True) # Remove the directory after the test

    def test_get_items(self):
        itens_actual = self.data_params._get_items()
        expected = [("param_name_2", "value_2"), ("param_name_1", "value_1")]

        self.assertEqual(expected, itens_actual)

    def test_add_items(self):
        self.data_params._add_items()

        self.assertEqual("value_1", self.data_params.properties["param_name_1"][0])
        self.assertEqual("value_2", self.data_params.properties["param_name_2"][0])

    def test_write_in_folder(self):
        name = "{}.properties".format(self.data_params.name)
        self.data_params._add_items()
        self.data_params._write(self.test_dir)
        f = open(path.join(self.test_dir, name))
        expected = "#name_teste_params.properties\nparam_name_1=value_1\nparam_name_2=value_2\n"

        self.assertEqual(f.read(), expected)


class EnvParamsTest(TestCase):

    def test_get_env_params(self):
        result_actual = Env(TESTE_HADOOP_NAME="hadoop", TESTE_SPARK_MASTER="yarn")._get_items()
        expected = [("env.TESTE_SPARK_MASTER", "yarn"), ("env.TESTE_HADOOP_NAME", "hadoop")]

        self.assertEqual(expected, result_actual)


class SparkExecutorParamsTest(TestCase):

    def test_get_spark_executor_params(self):
        result_actual = SparkExecutor(TESTE_HADOOP_NAME="hadoop", TESTE_SPARK_MASTER="yarn")._get_items()
        expected = [("TESTE_SPARK_MASTER", "--conf spark.executorEnv.TESTE_SPARK_MASTER=yarn"),
                    ("TESTE_HADOOP_NAME", "--conf spark.executorEnv.TESTE_HADOOP_NAME=hadoop")]

        self.assertEqual(expected, result_actual)


class SparkDriverParamsTest(TestCase):

    def test_get_spark_driver_params(self):
        result_actual = SparkDriver(TESTE_HADOOP_NAME="hadoop", TESTE_SPARK_MASTER="yarn")._get_items()
        expected = [("TESTE_SPARK_MASTER", "--conf spark.yarn.appMasterEnv.TESTE_SPARK_MASTER=yarn"),
                    ("TESTE_HADOOP_NAME", "--conf spark.yarn.appMasterEnv.TESTE_HADOOP_NAME=hadoop")]

        self.assertEqual(expected, result_actual)

class SparkConfigParamsTest(TestCase):

    def test_get_spark_driver_params(self):
        result_actual = SparkConfig(TESTE_HADOOP_NAME="hadoop", TESTE_SPARK_MASTER="yarn")._get_items()
        expected = [("TESTE_SPARK_MASTER", "--conf TESTE_SPARK_MASTER=yarn"),
                    ("TESTE_HADOOP_NAME", "--conf TESTE_HADOOP_NAME=hadoop")]

        self.assertEqual(expected, result_actual)


class ParamsJoinTest(TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.data_params = ParamsJoin("custom.env", " ")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_call_method(self):
        params_class = SparkDriver(TESTE_HADOOP_NAME="hadoop", TESTE_SPARK_MASTER="yarn")
        result_actual = self.data_params.__call__(params_class)
        expected = self.data_params.params_class

        self.assertEqual(expected, result_actual.params_class)

    def test_add_items(self):
        params_class = SparkDriver(TESTE_HADOOP_NAME="hadoop", TESTE_SPARK_MASTER="yarn")
        result_actual = self.data_params.__call__(params_class)
        result_actual._add_items()
        expected = "--conf spark.yarn.appMasterEnv.TESTE_SPARK_MASTER=yarn --conf spark.yarn.appMasterEnv.TESTE_HADOOP_NAME=hadoop"

        self.assertEqual(expected, result_actual.properties[result_actual.param_name][0])

    def test_write_in_folder(self):
        params_class = SparkDriver(TESTE_HADOOP_NAME="hadoop", TESTE_SPARK_MASTER="yarn")
        result_actual = self.data_params.__call__(params_class)
        name = "{}.properties".format("_".join([param_class.name for param_class in result_actual.params_class]))
        result_actual._add_items()
        result_actual._write(self.test_dir)
        f = open(path.join(self.test_dir, name))
        expected = "#params.properties\ncustom.env=--conf spark.yarn.appMasterEnv.TESTE_SPARK_MASTER\\=yarn --conf spark.yarn.appMasterEnv.TESTE_HADOOP_NAME\\=hadoop\n"

        self.assertEqual(f.read(), expected)

