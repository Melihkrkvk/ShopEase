from dataclasses import dataclass


@dataclass
class Product:
    """
    Domain object representing a product in the catalogue.

    Attributes:
        name (str): Product display name.
        price (float): Unit price in USD.
        stock (int): Available inventory count.
        category (str): Product category label.
        id (int | None): Assigned by the database after persistence.
    """

    name: str
    price: float
    stock: int
    category: str
    id: int | None = None
    image_url: str | None = None
    description: str | None = None
