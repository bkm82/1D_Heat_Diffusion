import pytest
import numpy as np
import scipy as sp
from solver.cartesian_mesh import CartesianMesh
import logging

logging.basicConfig(format="(levelname)s:%messages)s", level=logging.DEBUG)


@pytest.fixture
def differentation_matrix():
    def _differentiation_matrix(n):
        return sp.sparse.spdiags(
            np.array([np.ones(n), -2 * np.ones(n), np.ones(n)]), np.array([-1, 0, 1])
        ).toarray()

    return _differentiation_matrix


class Test_1d_CartesianMesh:
    @pytest.fixture
    def one_d_mesh(self):
        return CartesianMesh(dimensions=1, cordinates=[(0, 1)], n_cells=[4])

    def test_1d_cell_width(self, one_d_mesh):
        assert one_d_mesh.grid["x_grid"].cell_width == 0.25

    def test_1d_cell_cordinates(self, one_d_mesh):
        np.testing.assert_array_equal(
            x=one_d_mesh.grid["x_grid"].cell_cordinates,
            y=np.array([0.125, 0.375, 0.625, 0.875]),
        )

    def test_1d_differentiation_matrix(self, one_d_mesh, differentation_matrix):
        expected = differentation_matrix(4)
        np.testing.assert_array_equal(
            x=one_d_mesh.differentiation_matrix[
                "x_differentiation_matrix"
            ].get_matrix(),
            y=expected,
        )

    def test_1d_dirichlet_boundary_condition_array(self, one_d_mesh):
        expected = np.array([0, 0, 0, 0])
        np.testing.assert_array_equal(
            x=one_d_mesh.boundary_condition["x_boundary_condition_array"].get_array(),
            y=expected,
        )

    @pytest.mark.parametrize(
        "side,expected",
        [
            (
                "left",
                np.array([[-3, 1, 0, 0], [1, -2, 1, 0], [0, 1, -2, 1], [0, 0, 1, -2]]),
            ),
            (
                "right",
                np.array([[-2, 1, 0, 0], [1, -2, 1, 0], [0, 1, -2, 1], [0, 0, 1, -3]]),
            ),
        ],
    )
    def test_set_dirichlet_boundary_differentiaton_matrix(
        self, one_d_mesh, side, expected
    ):
        one_d_mesh.set_dirichlet_boundary(side=side, phi=30)
        actual = one_d_mesh.differentiation_matrix[
            "x_differentiation_matrix"
        ].get_matrix()
        np.testing.assert_array_equal(x=actual, y=expected)

    @pytest.mark.parametrize(
        "side,expected",
        [
            (
                "left",
                np.array([60, 0, 0, 0]),
            ),
            (
                "right",
                np.array([0, 0, 0, 60]),
            ),
        ],
    )
    def test_set_dirichlet_boundary_boundary_array(self, one_d_mesh, side, expected):
        one_d_mesh.set_dirichlet_boundary(side=side, phi=30)
        actual = one_d_mesh.boundary_condition["x_boundary_condition_array"].get_array()
        np.testing.assert_array_equal(x=actual, y=expected)

    @pytest.mark.parametrize(
        "side,expected",
        [
            (
                "left",
                np.array([30 * 0.25, 0, 0, 0]),
            ),
            (
                "right",
                np.array([0, 0, 0, 30 * 0.25]),
            ),
        ],
    )
    def test_set_neumann_boundary_boundary_array(self, one_d_mesh, side, expected):
        one_d_mesh.set_neumann_boundary(side=side, flux=30)
        actual = one_d_mesh.boundary_condition["x_boundary_condition_array"].get_array()
        np.testing.assert_array_equal(x=actual, y=expected)

    @pytest.mark.parametrize(
        "side,expected",
        [
            (
                "left",
                np.array([[-1, 1, 0, 0], [1, -2, 1, 0], [0, 1, -2, 1], [0, 0, 1, -2]]),
            ),
            (
                "right",
                np.array([[-2, 1, 0, 0], [1, -2, 1, 0], [0, 1, -2, 1], [0, 0, 1, -1]]),
            ),
        ],
    )
    def test_set_neumann_boundary_differentiaton_matrix(
        self, one_d_mesh, side, expected
    ):
        one_d_mesh.set_neumann_boundary(side=side, flux=30)
        actual = one_d_mesh.differentiation_matrix[
            "x_differentiation_matrix"
        ].get_matrix()
        np.testing.assert_array_equal(x=actual, y=expected)

    # Test a right neuiman, left dirichlet
    def test_laplacian_matrix(self, one_d_mesh):
        one_d_mesh.set_dirichlet_boundary(side="right", phi=30)
        one_d_mesh.set_neumann_boundary(side="left", flux=-10)
        # one_d_mesh.set_laplacian()
        expected = np.array(
            [[-1, 1, 0, 0], [1, -2, 1, 0], [0, 1, -2, 1], [0, 0, 1, -3]]
        ) * (1 / 0.25**2)
        np.testing.assert_array_equal(x=one_d_mesh.laplacian, y=expected)


class Test_2d_CartesianMesh:
    @pytest.fixture
    def two_d_mesh(self):
        return CartesianMesh(dimensions=2, cordinates=[(0, 1), (0, 2)], n_cells=[3, 4])

    cell_width_inputs = [("x_grid", 1 / 3), ("y_grid", 0.5)]

    @pytest.mark.parametrize("dimension,expected", cell_width_inputs)
    def test_2d_cell_width(self, two_d_mesh, dimension, expected):
        assert two_d_mesh.grid[dimension].cell_width == expected

    coordinates_inputs = [
        ("x_grid", np.array([1 / 6, 3 / 6, 5 / 6])),
        ("y_grid", np.array([0.25, 0.75, 1.25, 1.75])),
    ]

    @pytest.mark.parametrize("dimension,expected", coordinates_inputs)
    def test_2d_cell_cordinates(self, two_d_mesh, dimension, expected):
        np.testing.assert_array_equal(
            x=two_d_mesh.grid[dimension].cell_cordinates, y=expected
        )

    differentiation_matrix_inputs = [
        ("x_differentiation_matrix", 3),
        ("y_differentiation_matrix", 4),
    ]

    @pytest.mark.parametrize("dimension,n_cells", differentiation_matrix_inputs)
    def test_2d_cell_differentiation_matrix(
        self, two_d_mesh, dimension, n_cells, differentation_matrix
    ):
        # matrix = getattr(two_d_mesh, dimension)
        expected = differentation_matrix(n_cells)
        np.testing.assert_array_equal(
            x=two_d_mesh.differentiation_matrix[dimension].get_matrix(), y=expected
        )

    boundary_array_inputs = [
        ("x_boundary_condition_array", np.array([0, 0, 0])),
        ("y_boundary_condition_array", np.array([0, 0, 0, 0])),
    ]

    @pytest.mark.parametrize("dimension,expected", boundary_array_inputs)
    def test_2d_cell_boundary_condition_array(
        self, two_d_mesh, dimension, expected, differentation_matrix
    ):
        np.testing.assert_array_equal(
            x=two_d_mesh.boundary_condition[dimension].get_array(), y=expected
        )

    left_dirichlet_diff_matrix = np.array([[-3, 1, 0], [1, -2, 1], [0, 1, -2]])
    right_dirichlet_diff_matrix = np.array([[-2, 1, 0], [1, -2, 1], [0, 1, -3]])
    top_dirichlet_diff_matrix = np.array(
        [[-3, 1, 0, 0], [1, -2, 1, 0], [0, 1, -2, 1], [0, 0, 1, -2]]
    )
    bottom_dirichlet_diff_matrix = np.array(
        [[-2, 1, 0, 0], [1, -2, 1, 0], [0, 1, -2, 1], [0, 0, 1, -3]]
    )

    @pytest.mark.parametrize(
        "name,side,expected",
        [
            ("x_differentiation_matrix", "left", left_dirichlet_diff_matrix),
            ("x_differentiation_matrix", "right", right_dirichlet_diff_matrix),
            ("y_differentiation_matrix", "top", top_dirichlet_diff_matrix),
            ("y_differentiation_matrix", "bottom", bottom_dirichlet_diff_matrix),
        ],
    )
    def test_set_dirichlet_boundary_differentiaton_matrix(
        self, two_d_mesh, name, side, expected
    ):
        two_d_mesh.set_dirichlet_boundary(side=side, phi=30)
        # matrix = getattr(two_d_mesh, name)
        actual = two_d_mesh.differentiation_matrix[name].get_matrix()
        np.testing.assert_array_equal(x=actual, y=expected)

    left_dirichlet_bc_array = np.array([60, 0, 0])
    right_dirichlet_bc_array = np.array([0, 0, 60])
    top_dirichlet_bc_array = np.array([60, 0, 0, 0])
    bottom_dirichlet_bc_array = np.array([0, 0, 0, 60])

    @pytest.mark.parametrize(
        "name,side,expected",
        [
            ("x_boundary_condition_array", "left", left_dirichlet_bc_array),
            ("x_boundary_condition_array", "right", right_dirichlet_bc_array),
            ("y_boundary_condition_array", "top", top_dirichlet_bc_array),
            ("y_boundary_condition_array", "bottom", bottom_dirichlet_bc_array),
        ],
    )
    def test_set_dirichlet_boundary_boundary_array(
        self, two_d_mesh, name, side, expected
    ):
        two_d_mesh.set_dirichlet_boundary(side=side, phi=30)
        actual = two_d_mesh.boundary_condition[name].get_array()
        np.testing.assert_array_equal(x=actual, y=expected)

    left_neumann_diff_matrix = np.array([[-1, 1, 0], [1, -2, 1], [0, 1, -2]])
    right_neumann_diff_matrix = np.array([[-2, 1, 0], [1, -2, 1], [0, 1, -1]])
    top_neumann_diff_matrix = np.array(
        [[-1, 1, 0, 0], [1, -2, 1, 0], [0, 1, -2, 1], [0, 0, 1, -2]]
    )
    bottom_neumann_diff_matrix = np.array(
        [[-2, 1, 0, 0], [1, -2, 1, 0], [0, 1, -2, 1], [0, 0, 1, -1]]
    )

    @pytest.mark.parametrize(
        "name,side,expected",
        [
            ("x_differentiation_matrix", "left", left_neumann_diff_matrix),
            ("x_differentiation_matrix", "right", right_neumann_diff_matrix),
            # ("y_differentiation_matrix", "top", top_neumann_diff_matrix),
            # ("y_differentiation_matrix", "bottom", bottom_neumann_diff_matrix),
        ],
    )
    def test_set_neumann_boundary_differentiaton_matrix(
        self, two_d_mesh, name, side, expected
    ):
        two_d_mesh.set_neumann_boundary(side=side, flux=-10)
        # matrix = getattr(two_d_mesh, name)
        actual = two_d_mesh.differentiation_matrix[name].get_matrix()
        print(side)
        np.testing.assert_array_equal(x=actual, y=expected)

    left_neumann_bc_array = np.array([-10 / 3, 0, 0])
    right_neumann_bc_array = np.array([0, 0, -10 / 3])
    top_neumann_bc_array = np.array([-10 / 2, 0, 0, 0])
    bottom_neumann_bc_array = np.array([0, 0, 0, -10 / 2])

    @pytest.mark.parametrize(
        "name,side,expected",
        [
            ("x_boundary_condition_array", "left", left_neumann_bc_array),
            ("x_boundary_condition_array", "right", right_neumann_bc_array),
            ("y_boundary_condition_array", "top", top_neumann_bc_array),
            ("y_boundary_condition_array", "bottom", bottom_neumann_bc_array),
        ],
    )
    def test_set_neumann_boundary_boundary_array(
        self, two_d_mesh, name, side, expected
    ):
        two_d_mesh.set_neumann_boundary(side=side, flux=-10)
        actual = two_d_mesh.boundary_condition[name].get_array()
        np.testing.assert_array_almost_equal(x=actual, y=expected)

    # Test a mesh that was confirmed to be correct manually
    @pytest.fixture
    def steady_mesh(self):
        return CartesianMesh(dimensions=2, cordinates=[(0, 3), (0, 2)], n_cells=[3, 4])

    def test_laplacian_matrix(self, steady_mesh):
        steady_mesh.set_dirichlet_boundary(side="left", phi=30)
        steady_mesh.set_dirichlet_boundary(side="right", phi=30)
        steady_mesh.set_dirichlet_boundary(side="bottom", phi=30)
        steady_mesh.set_neumann_boundary(side="top", flux=-10)

        # one_d_mesh.set_laplacian()
        expected = np.array(
            [
                [-7.0, 1.0, 0.0, 4.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, -6.0, 1.0, 0.0, 4.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, -7.0, 0.0, 0.0, 4.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [4.0, 0.0, 0.0, -11.0, 1.0, 0.0, 4.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 4.0, 0.0, 1.0, -10.0, 1.0, 0.0, 4.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 4.0, 0.0, 1.0, -11.0, 0.0, 0.0, 4.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 4.0, 0.0, 0.0, -11.0, 1.0, 0.0, 4.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 4.0, 0.0, 1.0, -10.0, 1.0, 0.0, 4.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 4.0, 0.0, 1.0, -11.0, 0.0, 0.0, 4.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 4.0, 0.0, 0.0, -15.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 4.0, 0.0, 1.0, -14.0, 1.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 4.0, 0.0, 1.0, -15.0],
            ]
        )

        np.testing.assert_array_equal(x=steady_mesh.laplacian, y=expected)


class Test_CartesianMesh_exceptions:
    """Test features expected to raise an exception"""

    exception_inputs = [
        ({"dimensions": 3}),
        ({"dimensions": 2, "cordinates": [(0, 1)]}),
        ({"dimensions": 2, "n_cells": [5]}),
        ({"dimensions": 1}),
        ({"mesh_type": "finite_difference"}),
    ]

    @pytest.mark.parametrize("inputs", exception_inputs)
    def test_three_dimensions_raises(self, inputs):
        with pytest.raises(ValueError):
            CartesianMesh(**inputs)
