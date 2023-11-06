from solver.mesher import grid, differentiation_matrix, boundary_condition
from typing import Sequence, Tuple, List


class cartesian_mesh:
    """
    A cartesian mesh up to 2D.

    Atributes:
    dimensions: int =  Number of dimensions (1d or 2d)
    n_cells:List[int]: Number of cells to discritize each dimension
    cordinates:Sequence[Tuple[float, float]] = The bounds each dimension
    mesh_type: str = The mesh type. currently only finite_volume.

    Example:
    To create a 2d mesh with
        3 cells in the x axis going from 0 to 1
        4 cells in the y axis going from 0 to 2
        cartesian_mesh(
            dimensions = 2
            n_cells = [3, 4]
            cordinates = [(0,1), (0,2)]
    """

    def __init__(
        self,
        dimensions: int = 2,
        n_cells: List[int] = [4, 4],
        cordinates: Sequence[Tuple[float, float]] = [(0, 1), (0, 1)],
        mesh_type: str = "finite_volume",
    ) -> None:
        """
        Init the cartesian mesh object.

        Args:
            dimensions:int = Mesh dimensionality (default 2d)
            cordinates (list of tupples):list of each dimensions cordinates
            mesh_type: str = finite_volume (default) or finite_difference

        """
        self.validate_inputs(n_cells, cordinates, dimensions, mesh_type)
        self.n_cells = n_cells
        self.dimensions = dimensions
        self.cordinates = cordinates
        self.mesh_type = mesh_type
        self.discritize()

    def validate_inputs(
        self,
        n_cells: List[int] = [4, 4],
        cordinates: Sequence[Tuple[float, float]] = [(0, 1), (0, 1)],
        dimensions: int = 2,
        mesh_type: str = "finite_volume",
    ) -> None:
        """
        Validate the cartesian mesh inputs.

        Args:
            dimensions:int = Mesh dimensionality (default 2d)
            cordinates (list of tupples):list of each dimensions cordinates
            mesh_type: str = finite_volume (default) or finite_difference

        """
        # Implemented dimensions and mesh types
        self.implemented_dimensions: Tuple[str, str] = ("x", "y")
        self.implemented_mesh_types: str = "finite_volume"

        if dimensions > len(self.implemented_dimensions):
            raise ValueError("mesh dimesnionality not implemented")

        # Validate cordinates were given for each dimension
        if len(cordinates) != dimensions:
            raise ValueError("number of cordinates needs to match dimesnions")
        if len(n_cells) != dimensions:
            raise ValueError("legth of n_cells list needs to match dimension")

        if mesh_type not in self.implemented_mesh_types:
            raise ValueError(f"{mesh_type}: is not an implemented mesh")

    def discritize(self):
        """Discritize the mesh for each axis dimension."""
        grid_list = self.create_atribute_list("grid")
        matrix_list = self.create_atribute_list("differentiation_matrix")
        boundary_array_list = self.create_atribute_list("boundary_condition_array")

        for index, (
            grid_name,
            differentiation_matrix_name,
            boundary_array_name,
        ) in enumerate(zip(grid_list, matrix_list, boundary_array_list)):
            setattr(
                self,
                grid_name,
                grid(
                    n_cells=self.n_cells[index],
                    cordinates=self.cordinates[index],
                    mesh_type=self.mesh_type,
                ),
            )

            setattr(
                self,
                differentiation_matrix_name,
                differentiation_matrix(
                    n_cells=self.n_cells[index],
                ),
            )

            setattr(
                self,
                boundary_array_name,
                boundary_condition(
                    n_cells=self.n_cells[index], mesh_type=self.mesh_type
                ),
            )

    def create_atribute_list(self, atribute_name: str) -> List[str]:
        """
        Create a list of of atributes for each active dimension.

        args:
        atribute_name:str the atribute name you would like in teh list

        example:
        create_atribute_list (differentation_matrix) with dimensions = 2
        returns ["x_differentiation_matrix", "y_differentiation_matrix"]
        """
        attribute_list: List[str] = []
        for index, dim in enumerate(self.implemented_dimensions):
            if index <= self.dimensions - 1:
                attribute_list.insert(index, f"{dim}_{atribute_name}")

        return attribute_list
