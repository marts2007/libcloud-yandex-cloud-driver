import yaml
import os

from yandex.cloud.compute.v1.instance_pb2 import Instance

from libcloud.compute.base import NodeAuthSSHKey, NodeDriver, Node, NodeState, NodeImage, NodeSize
from libcloud.compute.types import Provider, LibcloudError
from libcloud_yandex import YandexCloudApi

from yandex.cloud.compute.v1.instance_service_pb2 import (
    ListInstancesRequest,
    CreateInstanceRequest,
    CreateInstanceMetadata,
    ResourcesSpec,
    AttachedDiskSpec
)

NODE_STATE_MAP = {
    "PROVISIONING": NodeState.PENDING,
    1: NodeState.PENDING,
    "RUNNING": NodeState.RUNNING,
    2: NodeState.RUNNING,
    "STOPPING": NodeState.STOPPING,
    3: NodeState.STOPPING,
    "STOPPED": NodeState.STOPPED,
    4: NodeState.STOPPED,
    "STARTING": NodeState.STARTING,
    5: NodeState.STARTING,
    "RESTARTING": NodeState.REBOOTING,
    6: NodeState.REBOOTING,
    "UPDATING": NodeState.RECONFIGURING,
    7: NodeState.RECONFIGURING,
    "ERROR": NodeState.ERROR,
    8: NodeState.ERROR,
    "CRASHED": NodeState.ERROR,
    9: NodeState.ERROR,
    "DELETING": NodeState.STOPPING,
    10: NodeState.STOPPING
}


class YandexNodeDriver(NodeDriver):
    name = "yandex-cloud"
    fodler_id = None
    zone_id = None
    key = None
    api = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert 'folder_id' in kwargs
        self.folder_id = kwargs.get('folder_id')
        assert 'key' in kwargs
        self.api = YandexCloudApi(auth_key_path=kwargs.get('key'))
        self.zone_id = kwargs.get('zone_id', 'ru-central1-a')
        assert 'subnet_id' in kwargs
        self.subnet_id = kwargs.get('subnet_id')

    def list_sizes(self, location=None):
        module_dir = os.path.dirname(os.path.abspath(__file__))
        with open(f'{module_dir}/compute_sizes.yaml', 'r') as yaml_file:
            yaml_content = yaml.safe_load(yaml_file)
        assert yaml_content.get('compute_node_sizes')
        if os.path.isfile('compute_sizes.yaml'):
            with open(f'compute_sizes.yaml', 'r') as yaml_file:
                yaml_content = yaml.safe_load(yaml_file)
        return list(map(self._to_size, yaml_content.get('compute_node_sizes')))

    def list_nodes(self, *args, **kwargs):  # type: (Any, Any) -> List[Node]
        result = []
        nodes = self.api.get_compute_instances(folder_id=self.folder_id)
        return list(map(self._to_node, nodes.instances))

    def list_images(self, location=None, *args, **kwargs):
        """
        List images on YandexCloud Repositories

        :keyword location: The location to list images for.
        :type    location: :class:`NodeLocation`

        :return:           list of node image objects
        :rtype:            ``list`` of :class:`NodeImage`
        """
        result = []
        folder_id = kwargs.get("folder_id", self.folder_id)
        images_result = self.api.list_images(folder_id=folder_id)
        return list(map(self._to_image, images_result.images))

    def create_image(self, image_url):
        """
        Create image from s3 bucket url
        README https://cloud.yandex.ru/docs/compute/operations/image-create/custom-image
        :param image_url:
        :return:         image object
        """
        image = self.api.create_image(self.folder_id, image_url)
        return self._to_image(image.response)

    def create_address(self):
        return self.api.create_address(folder_id=self.folder_id)

    def list_addresses(self):
        return self.api.list_address(folder_id=self.folder_id)

    def create_node(
        self,
        name,  # type: str
        size,  # type: NodeSize
        image,  # type: NodeImage,
        location=None,  # type: Optional[NodeLocation]
        auth=None,  # type: Optional[T_Auth],
    ):
        # type: (...) -> Node
        ssh_key=None
        if isinstance(auth,NodeAuthSSHKey):
            ssh_key = auth.pubkey
        result = self.api.create_instance(
            name=name,
            folder_id=self.folder_id,
            platform_id=size.extra.get('platform_id', 'standard-v3'),
            resources_spec=ResourcesSpec(
                memory=size.ram,
                cores=size.extra.get('cores',4),
                gpus=size.extra.get('gpus',0)
            ),
            boot_disk_spec=AttachedDiskSpec(
                auto_delete=True,
                disk_spec=AttachedDiskSpec.DiskSpec(
                    size=image.extra.get('min_disk_size','20971520000'),
                    image_id=image.id
                )
            ),
            subnet_id=self.subnet_id,
            zone_id=self.zone_id,
            ssh_key = ssh_key
        )
        return self._to_node(result.response)

    def destroy_node(self, node: Node):
        return self.api.delete_instance(node.id)

    def _to_image(self, image):
        extra = {
            "folder_id": image.folder_id,
            "created_at": image.created_at,
            "storage_size": image.storage_size,
            "min_disk_size": image.min_disk_size,
            "status": image.status,
            "os": image.os,
            "min_disk_size": image.min_disk_size
        }
        return NodeImage(id=image.id, name=image.id, driver=self, extra=extra)

    def _to_node(self, instance: Instance):
        identifier = instance.id
        name = instance.name
        state = NODE_STATE_MAP[instance.status]
        link_image = ""
        private_ips = [instance.network_interfaces[0].primary_v4_address.address]
        public_ips = [instance.network_interfaces[0].primary_v4_address.one_to_one_nat.address]
        return Node(
            identifier,
            name,
            state,
            public_ips,
            private_ips,
            self
        )

    def _to_size(self, size):
        ns = NodeSize(
            id=size.get('name'),
            name=size.get('name'),
            ram=size.get('memory')*1024*1024*1024,
            disk=size.get('drive', 20),
            bandwidth=None,
            price=None,
            driver=self.connection.driver,
            extra={
                'cores': size.get('cores', None),
                'platform_id': size.get('platform_id', None)
            }
        )
        return ns
