# Import all models here so that Base.metadata is fully populated.
# This ensures Base.metadata.create_all() and Alembic autogenerate
# can discover every table.

from models.node_type import NodeType
from models.edge_type import EdgeType
from models.node_property_definition import NodePropertyDefinition
from models.edge_property_definition import EdgePropertyDefinition
from models.node_type_property_assignment import NodeTypePropertyAssignment
from models.edge_type_property_assignment import EdgeTypePropertyAssignment
from models.node import Node
from models.edge import Edge
from models.node_property_value import NodePropertyValue
from models.edge_property_value import EdgePropertyValue
