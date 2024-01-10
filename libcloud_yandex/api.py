# import libcloud_yandex
import os
import grpc
import json

import yandexcloud

from yandex.cloud.compute.v1.instance_service_pb2_grpc \
    import InstanceServiceStub

from yandex.cloud.compute.v1.image_service_pb2_grpc \
    import ImageServiceStub
from yandex.cloud.compute.v1.image_service_pb2 import (
     ListImagesRequest,
     CreateImageRequest,
     CreateImageMetadata,

     )
from yandex.cloud.vpc.v1.address_service_pb2 import (
    CreateAddressRequest,
    ExternalIpv4AddressSpec,
    CreateAddressMetadata,
    ListAddressesRequest
)
from yandex.cloud.vpc.v1.address_pb2 import ExternalIpv4Address, Address
from yandex.cloud.vpc.v1.address_service_pb2_grpc import AddressServiceStub
from yandex.cloud.compute.v1.image_pb2 import Image
from yandex.cloud.compute.v1.instance_pb2 import Instance
from yandex.cloud.compute.v1.instance_service_pb2 import (
    ListInstancesRequest,
    CreateInstanceRequest,
    CreateInstanceMetadata,
    ResourcesSpec,
    AttachedDiskSpec,
    NetworkInterfaceSpec,
    PrimaryAddressSpec,
    OneToOneNatSpec,
    DeleteInstanceRequest,
    DeleteInstanceMetadata
)


class YandexCloudApi:
    auth_key_path=None

    def __init__(self, auth_key_path):
        self.auth_key_path=auth_key_path
        self.interceptor = yandexcloud.RetryInterceptor(
            max_retry_count=5, retriable_codes=[grpc.StatusCode.UNAVAILABLE])
        with open(self.auth_key_path, 'r') as private:
            sa_key = json.loads(private.read())  # Чтение закрытого ключа из файла.
        self.sdk = yandexcloud.SDK(
            service_account_key=sa_key
        )

    def get_compute_instances(self, folder_id):

        instance_service = self.sdk.client(InstanceServiceStub)
        result = instance_service.List(ListInstancesRequest(
            folder_id=folder_id,
        ))
        return result

    def list_images(self, folder_id):
        instance_service = self.sdk.client(ImageServiceStub)
        result = instance_service.List(ListImagesRequest(
            folder_id=folder_id,
        ))
        return result

    def create_image(self, folder_id, image_url):
        result = self.sdk.create_operation_and_get_result(
            CreateImageRequest(
                folder_id=folder_id,
                uri=image_url
            ),
            service=ImageServiceStub,
            response_type=Image,
            method_name="Create",
            meta_type=CreateImageRequest
        )
        return result

    def create_address(self, folder_id: str):
        result = self.sdk.create_operation_and_get_result(
            CreateAddressRequest(
                folder_id=folder_id,
                external_ipv4_address_spec=ExternalIpv4AddressSpec(
                    zone_id="ru-central1-a"
                )
            ),
            service=AddressServiceStub,
            method_name="Create",
            meta_type=CreateAddressMetadata,
            response_type=Address
        )
        return result

    def list_address(self, folder_id: str):
        address_service = self.sdk.client(AddressServiceStub)
        result = address_service.List(ListAddressesRequest(
            folder_id=folder_id,
        ))
        return result

    def create_instance(self,
                        folder_id: str,
                        zone_id: str,
                        platform_id: str,
                        subnet_id: str,
                        resources_spec: ResourcesSpec,
                        boot_disk_spec: AttachedDiskSpec,
                        name: str = None,
                        description: str = None,
                        ssh_key: str = None
                        ):
        result = self.sdk.create_operation_and_get_result(
            CreateInstanceRequest(
                folder_id=folder_id,
                name=name,
                description=description,
                zone_id=zone_id,
                platform_id=platform_id,
                resources_spec=resources_spec,
                boot_disk_spec=boot_disk_spec,
                network_interface_specs=[
                    NetworkInterfaceSpec(
                        subnet_id=subnet_id,
                        primary_v4_address_spec=PrimaryAddressSpec(
                            one_to_one_nat_spec=OneToOneNatSpec(
                                ip_version="IPV4",
                            )
                        )
                    )
                ],
                metadata={
                    "user-data":f"#cloud-config\nusers:\n  - name: libcloud\n    groups: sudo\n    shell: /bin/bash\n    sudo: 'ALL=(ALL) NOPASSWD:ALL'\n    ssh-authorized-keys:\n      - {ssh_key}"
                }
            ),
            service=InstanceServiceStub,
            response_type=Instance,
            meta_type=CreateInstanceMetadata,
            method_name="Create"
        )
        return result

    def delete_instance(self, instance_id):
        result = self.sdk.create_operation_and_get_result(
            DeleteInstanceRequest(
                instance_id=instance_id
            ),
            service=InstanceServiceStub,
            method_name="Delete",
            meta_type=DeleteInstanceMetadata,
        )
        return result
