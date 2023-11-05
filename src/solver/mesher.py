import numpy as np
import scipy


class create_1Dmesh:
    """
    A class representing a 1D Mesh.

    Atributes:
    xcell_center (np.array): An array of node x positions
    n_points (int): The number of mesh points
    delta_x (float) : The distance between mesh points

    """

    def __init__(self, x, n_cells, mesh_type="finite_volume"):
        """
        Initialize the Mesh object.

        Keyword Arguments:
        x -- the spatial domain of the mesh in the form [x_min, x_max]
        n_cells -- the number of points for discritization.
        use n_cells as the number of points for the finite volume case

        Example
        mesh = create_1Dmesh(x=[0, 1], n_cells=3)
        mesh.xcell_center = np.array([0.125,0.375, 0.625, 0.875])
        mesh.deltax = 0.25
        """
        self.n_cells = n_cells
        self.mesh_type = mesh_type
        x_grid = grid(n_cells, x, mesh_type)

        self.delta_x = x_grid.cell_width
        self.xcell_center = x_grid.cell_cordinates
        self.x_differentiation_matrix = differentiation_matrix(self.n_cells)
        self.laplacian_matrix = self.x_differentiation_matrix.get_matrix()
        self.boundary_condition_object = boundary_condition(
            n_cells=self.n_cells, mesh_type=self.mesh_type
        )
        self.boundary_condition_array = (
            self.boundary_condition_object.boundary_condition_array
        )


class heat_diffusion_mesh(create_1Dmesh):
    """Create a heat diffusion mesh."""

    def __init__(self, x, n_cells: int, mesh_type: str = "finite_volume"):
        """
        Initialize a heat diffusion mesh object.

        Parameters:
           x (type) : the spatial discritization of the domain
           n_cells (int): The number of cells to discritize the domain into
           mesh_type (string) : finite_volume (default) or finite_difference
        """
        super().__init__(x, n_cells, mesh_type)
        self.temperature = np.zeros(n_cells)

    def set_cell_temperature(self, temperature):
        """
        Set the temperature for internal nodes.

        Example:running mesh.set_internal_temperature(20) would result
        in np.array([20, 20, 20, 20]
        """
        self.temperature = temperature * np.ones(self.n_cells)

    def set_thermal_diffusivity(self, thermal_diffusivity):
        """Set a diffusion constant in square meters per second."""
        self.thermal_diffusivity = thermal_diffusivity

    def set_dirichlet_boundary(self, side, temperature):
        """Update boundary array and D2 for a dirichlet boundary."""
        self.x_differentiation_matrix.set_dirichlet_boundary(side, self.mesh_type)
        self.boundary_condition_object.set_dirichlet_boundary(
            side=side, phi=temperature
        )
        array_index = side_selector().boundary_index(side)

        if self.mesh_type == "finite_volume":
            pass
        elif self.mesh_type == "finite_difference":
            self.temperature[array_index] = temperature
        else:
            raise ValueError("mesh must be finite_volume or finite_difference")

    def set_neumann_boundary(self, side, flux=0):
        """Update boundary array and D2 for a neumann boundary."""

        self.x_differentiation_matrix.set_neumann_boundary(side, self.mesh_type)
        # self.boundary_condition_object.set_neumann_boundary(side = side, phi = temperature)

        if side == "left":
            array_index = 0
        elif side == "right":
            array_index = -1
        else:
            raise ValueError("Side must input must be left or right")

        if self.mesh_type == "finite_volume":
            self.boundary_condition_array[array_index] = flux / self.delta_x
        elif self.mesh_type == "finite_difference":
            self.boundary_condition_array[array_index] = 2 * flux * self.delta_x
        else:
            raise ValueError(
                "mesh_type unsupported, please input a finite_volume or finite_difference as mesh type"
            )


class linear_convection_mesh(create_1Dmesh):
    """
    Create a linear convection diffusion mesh.

    Attributes:
    n_cells (int): The number of cells used to discritze the domain
    mesh_type (str): finite_volume or finite_difference
    """

    def __init__(
        self,
        x,
        n_cells: int,
        mesh_type: str = "finite_volume",
        convection_coefficient=1,
        discretization_type: str = "upwind",
    ):
        """
        Initialize a lienar convection mesh object.

        Parameters:
           x : the spatial discritization of the domain
           n_cells (int): The number of cells to discritize the domain into
           mesh_type (string) : finite_voluem (default) or finite_difference
        Attributes:
           phi: the quantity of interest being transported
           convection_coefficent: a constant convection coefficent
        """
        super().__init__(x, n_cells, mesh_type)

        self.discretization_type = discretization_type
        if self.discretization_type == "upwind":
            self.x_differentiation_matrix = upwind_differentiation_matrix(self.n_cells)

        elif self.discretization_type == "central":
            self.x_differentiation_matrix = central_differentiation_matrix(self.n_cells)

        elif self.discretization_type == "maccormack":
            # self.create_maccormack_differentiation_matrix(self.xcell_center)
            self.x_differentiation_matrix = maccormack_differentiation_matrix(
                self.n_cells
            )

            self.predictor_differentiation_matrix = (
                self.x_differentiation_matrix.predictor_differentiation_matrix
            )
        else:
            raise ValueError("discritization type not supported")

        self.laplacian_matrix = self.x_differentiation_matrix.get_matrix()

        if convection_coefficient <= 0:
            raise ValueError("only positive convection coefficents are supported")
        self.convection_coefficent = convection_coefficient
        self.phi = np.zeros(n_cells)

    def set_phi(self, phi):
        """
        Set the value of phi for internal nodes.

        Parameters:
        phi (int, float, list):list of phi at every x value
        """
        if isinstance(phi, (float, int)):
            self.phi = phi * np.ones(self.n_cells)
        elif isinstance(phi, list):
            if np.array(phi).shape != self.xcell_center.shape:
                raise ValueError("the shape of phi must match the xcell_center shape")
            self.phi = np.array(phi)
        else:
            raise TypeError("The phi type inputed not supported")

    def set_dirichlet_boundary(self, side: str, phi: float):
        """Update boundary array and D2 for a dirichlet boundary."""
        self.x_differentiation_matrix.set_dirichlet_boundary(side, self.mesh_type)
        if side == "left":
            array_index = 0

        else:
            raise ValueError("Only left side implemented")

        if self.mesh_type == "finite_volume":
            self.boundary_condition_array[array_index] = phi
            self.laplacian_matrix[array_index, array_index] = -1
        elif self.mesh_type == "finite_difference":
            self.boundary_condition_array[array_index] = 0
            if self.discretization_type == "maccormack":
                self.predictor_differentiation_matrix[array_index, :] = 0
            self.phi[array_index] = phi
        else:
            raise ValueError("mesh must be finite_volume or finite_difference")

    def set_right_boundary(self):
        """
        Set the differentiation matrix using a 2nd order left discritization.

        For finite volume only
        """
        self.laplacian_matrix[-1, -3:] = [1.5, -1, 0.5]


class differentiation_matrix:
    """Create a differentiation matrix."""

    def __init__(self, n_cells: int):
        """
        Initialaze a differentiation  matrix.

        Paramaters: n_cells number of cells
        Atributes:
        differentiation_matrix: A sparse  matrix n_cells x n_cells with -2 on the diagonal and a 1 on the +1 and -1 diagonal

        """
        self.__n_cells = n_cells
        self.differentiation_matrix = self.set_diagonal()

    def get_matrix(self):
        """Return: differentiation matrix."""
        return self.differentiation_matrix

    def set_diagonal(self, lower=1, middle=-2, upper=1):
        """Create a sparce diagonal matrix"""
        self.diagonal = np.ones(self.__n_cells)
        return scipy.sparse.spdiags(
            np.array(
                [lower * self.diagonal, middle * self.diagonal, upper * self.diagonal]
            ),
            np.array([-1, 0, 1]),
        ).toarray()

    def set_dirichlet_boundary(self, side, mesh_type):
        """Update boundary array and D2 for a dirichlet boundary."""
        array_index = side_selector().boundary_index(side)

        if mesh_type == "finite_volume":
            self.differentiation_matrix[array_index, array_index] = -3

        elif mesh_type == "finite_difference":
            self.differentiation_matrix[array_index, :] = 0
        else:
            raise ValueError("mesh must be finite_volume or finite_difference")

    def set_neumann_boundary(self, side, mesh_type):
        """Update the differentiation matrix for a neumann boundary."""
        boundary_index = side_selector().boundary_index(side)
        first_interior_index = side_selector().first_interior_index(side)

        if mesh_type == "finite_volume":
            self.differentiation_matrix[boundary_index, boundary_index] = -1
        elif mesh_type == "finite_difference":
            self.differentiation_matrix[boundary_index, first_interior_index] = 2
        else:
            raise ValueError(
                "mesh_type unsupported, please input a finite_volume or finite_difference as mesh type"
            )


class upwind_differentiation_matrix(differentiation_matrix):
    def __init__(self, n_cells: int):
        """Create a differentiation matrix."""
        super().__init__(n_cells)
        self.differentiation_matrix = self.set_diagonal(lower=1, middle=-1, upper=0)


class central_differentiation_matrix(differentiation_matrix):
    def __init__(self, n_cells: int):
        """Create a differentiation matrix."""
        super().__init__(n_cells)
        self.differentiation_matrix = self.set_diagonal(lower=0.5, middle=0, upper=-0.5)


class maccormack_differentiation_matrix(differentiation_matrix):
    def __init__(self, n_cells: int):
        super().__init__(n_cells)
        self.differentiation_matrix = self.set_diagonal(lower=-1, middle=1, upper=0)

        self.predictor_differentiation_matrix = -np.transpose(
            self.differentiation_matrix
        )


class grid:
    """
    A 1d uniformly discritzed grid object.

    Attributes:
        cordinates:
        delta:
    """

    def __init__(
        self, n_cells: int, cordinates: tuple[float, float], mesh_type: str
    ) -> None:
        """
        Args:
            n_cells: int = number of cells to discritize the grid
            cordinates: tupple(float, float) = min and max of the grid
            mesh_type (string)=  finite_volume or finite_difference
        """
        self.n_cells = n_cells
        self.cordinates = cordinates
        self.__discritize(mesh_type)

    def __discritize(self, mesh_type):
        if mesh_type == "finite_volume":
            self.cell_width = (self.cordinates[1] - self.cordinates[0]) / (self.n_cells)
            self.cell_cordinates = np.linspace(
                self.cordinates[0] + (self.cell_width / 2),
                self.cordinates[1] - self.cell_width / 2,
                self.n_cells,
            )
        elif mesh_type == "finite_difference":
            self.cell_width = (self.cordinates[1] - self.cordinates[0]) / (
                self.n_cells - 1
            )
            self.cell_cordinates = np.linspace(
                self.cordinates[0], self.cordinates[1], self.n_cells
            )
        else:
            raise ValueError("Mesh type not supported")


class boundary_condition:
    """
    A boundary condition object.

    Attributes
        boundary_condition_array: array[float]
    """

    def __init__(self, n_cells: int, mesh_type: str):
        self.boundary_condition_array = np.zeros(n_cells)
        mesh_type_validator().validate(mesh_type)
        self.__mesh_type = mesh_type

    def set_dirichlet_boundary(self, side: str, phi: float):
        """Update the boundary contition array for a dirichlet boundary"""
        boundary_index = side_selector().boundary_index(side)
        if self.__mesh_type == "finite_volume":
            self.boundary_condition_array[boundary_index] = 2 * phi
        elif self.__mesh_type == "finite_difference":
            self.boundary_condition_array[boundary_index] = 0


class side_selector:
    """Set the array index to modify based on the boundary side."""

    def boundary_index(self, side: str):
        """Return the index for the first or last row (or column) based on the side."""
        if side == "left":
            return 0
        elif side == "right":
            return -1
        else:
            raise ValueError("Side must input must be left or right")

    def first_interior_index(self, side: str):
        """Return the index for the first interior cell (1, or -2)."""
        if side == "left":
            return 1
        elif side == "right":
            return -2
        else:
            raise ValueError("Side must input must be left or right")


class mesh_type_validator:
    """Validate that the mesh type is supported."""

    def validate(self, mesh_type: str):
        """ensures that the mesh type is either a "finite_volume" or "finite_difference"""
        if mesh_type not in ("finite_volume", "finite_difference"):
            raise ValueError("Side must input must be left or right")


def main():
    pass


def init():
    if __name__ == "__main__":
        main()


init()
