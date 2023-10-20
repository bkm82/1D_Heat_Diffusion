import pytest
import numpy as np

from solver.mesher import create_1Dmesh


# @pytest.fixture
# def three_point_mesh():
#     return create_1Dmesh(x=[0, 1], n_cells=3)


@pytest.fixture
def four_cell_mesh():
    return create_1Dmesh(x=[0, 1], n_cells=4)


def test_1dmesh_discritize(four_cell_mesh):
    assert np.array_equal(
        four_cell_mesh.xcell_center, np.array([0.125, 0.375, 0.625, 0.875])
    )


def test_set_deltax(four_cell_mesh):
    assert four_cell_mesh.delta_x == 0.25


def test_set_n_cells(four_cell_mesh):
    assert four_cell_mesh.n_cells == 4


def test_set_differentiation_matrix(four_cell_mesh):
    expected_differentiation_matrix = np.array(
        [[-2, 1, 0, 0], [1, -2, 1, 0], [0, 1, -2, 1], [0, 0, 1, -2]]
    )

    assert np.array_equal(
        four_cell_mesh.differentiation_matrix, expected_differentiation_matrix
    )


# def test_initialize_temperature_vector(four_cell_mesh):
#     expected_temperature = np.array([0, 0, 0, 0])
#     assert np.array_equal(four_cell_mesh.temperature, expected_temperature)


# def test_initialize_four_point_temperature_vector(four_cell_mesh):
#     expected_temperature = np.array([0, 0, 0, 0])
#     assert np.array_equal(four_point_mesh.temperature, expected_temperature)


def test_internal_initial_temperature(four_cell_mesh):
    four_cell_mesh.set_cell_temperature(20)

    assert np.array_equal(four_cell_mesh.temperature, np.array([20, 20, 20, 20]))
