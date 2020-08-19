# Copyright 2019-2020 The AmpliGraph Authors. All Rights Reserved.
#
# This file is Licensed under the Apache License, Version 2.0.
# A copy of the Licence is available in LICENCE, or at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
import os
import importlib
import numpy as np
import pandas as pd
import numpy.testing as npt
from ampligraph.utils import save_model, restore_model, create_tensorboard_visualizations, \
                             write_metadata_tsv, dataframe_to_triples
from ampligraph.latent_features import TransE
import pytest


def test_save_and_restore_model():

    models = ('ComplEx', 'TransE', 'DistMult')

    for model_name in models:
        module = importlib.import_module("ampligraph.latent_features.models")

        print('Doing save/restore testing for model class: ', model_name)

        class_ = getattr(module, model_name)

        model = class_(batches_count=2, seed=555, epochs=20, k=10,
                       optimizer='adagrad', optimizer_params={'lr': 0.1})

        X = np.array([['a', 'y', 'b'],
                      ['b', 'y', 'a'],
                      ['a', 'y', 'c'],
                      ['c', 'y', 'a'],
                      ['a', 'y', 'd'],
                      ['c', 'y', 'd'],
                      ['b', 'y', 'c'],
                      ['f', 'y', 'e']])

        model.fit(X)

        example_name = 'helloworld.pkl'

        save_model(model, model_name_path = example_name)

        loaded_model = restore_model(model_name_path = example_name)

        assert loaded_model is not None
        assert loaded_model.all_params == model.all_params
        assert loaded_model.is_fitted == model.is_fitted
        assert loaded_model.ent_to_idx == model.ent_to_idx
        assert loaded_model.rel_to_idx == model.rel_to_idx

        for i in range(len(loaded_model.trained_model_params)):
            npt.assert_array_equal(loaded_model.trained_model_params[i], model.trained_model_params[i])

        y_pred_before = model.predict(np.array([['f', 'y', 'e'], ['b', 'y', 'd']]))
        y_pred_after = loaded_model.predict(np.array([['f', 'y', 'e'], ['b', 'y', 'd']]))
        npt.assert_array_equal(y_pred_after, y_pred_before)

        npt.assert_array_equal(loaded_model.get_embeddings(['a', 'b'], embedding_type='entity'),
                               model.get_embeddings(['a', 'b'], embedding_type='entity'))

        os.remove(example_name)


def test_restore_model_errors():

    with pytest.raises(FileNotFoundError):
        model = restore_model(model_name_path='filenotfound.model')


def test_create_tensorboard_visualizations():
    # test if tensorflow API are still operative

    X = np.array([['a', 'y', 'b'],
                  ['b', 'y', 'a'],
                  ['a', 'y', 'c'],
                  ['c', 'y', 'a'],
                  ['a', 'y', 'd'],
                  ['c', 'y', 'd'],
                  ['b', 'y', 'c'],
                  ['f', 'y', 'e']])
    model = TransE(batches_count=1, seed=555, epochs=20, k=10, loss='pairwise',
                   loss_params={'margin': 5})
    model.fit(X)
    create_tensorboard_visualizations(model, 'tensorboard_files')


def test_write_metadata_tsv():
    # TODO: This
    pass


def test_dataframe_to_triples():
    X = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')
    schema = [('species', 'has_sepal_length', 'sepal_length')]
    npt.assert_array_equal(dataframe_to_triples(X, schema)[0], 
                           np.array(['setosa', 'has_sepal_length', '5.1']))
    
    schema = [('species', 'has_sepal_length', 'abc')]
    try:
        dataframe_to_triples(X, schema)
    except:
        assert True
    
    schema = [('species', 'has_sepal_length', 'sepal_length')]
    try:
        dataframe_to_triples(X, schema)
    except:
        assert True
