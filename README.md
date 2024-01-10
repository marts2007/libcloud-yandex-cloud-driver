# libcloud-yandex-cloud-driver
### example
```bash
import os

from libcloud.compute.providers import get_driver, set_driver
from libcloud.compute.base import NodeAuthSSHKey


set_driver('libcloud_yandex', 'libcloud_yandex', 'YandexNodeDriver')
driver = get_driver("libcloud_yandex")
client = driver(
    # service account key path (please remove "PLEASE DO NOT REMOVE THIS LINE! Yandex.Cloud SA Key ID <>" substring from the keyfile)
    key='{}/.ssh/yacloud/authorized_key.json'.format(os.path.expanduser('~')),  # path to auth_key json file
    # yandex cloud folder id
    folder_id='',  # yandex cloud folder id
    # zone_id you would like to use
    zone_id = 'ru-central1-a',  # zone to use
    # subnet_id - please get the id from the yandex cloud console
    # https://console.cloud.yandex.com/folders/<folder_id>/vpc/subnets
    subnet_id=''  # subnet id
)


nodes = client.list_nodes()
print(nodes)


# To create custom OS image please check the README
# https://cloud.yandex.ru/docs/compute/operations/image-create/custom-image
# image = client.create_image(
#     image_url="https://storage.yandexcloud.net/shipstorage/test.img?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=kE1XodE2fCs8q4xF6ttD%2F20231215%2Fru-central1%2Fs3%2Faws4_request&X-Amz-Date=20231215T085453Z&X-Amz-Expires=2592000&X-Amz-Signature=D61A0E62C1FED8FD9460F741732D2684838838061F3DAAF3151C691C03F042DC&X-Amz-SignedHeaders=host"
# )

# node sizes templates ("compute_sizes.yaml")
sizes = client.list_sizes()

# folder_id "standard-images" to get images from the cloud marketplace
# https://cloud.yandex.ru/docs/compute/operations/images-with-pre-installed-software/get-list
images = client.list_images(folder_id='standard-images')

image = images[0]  # let`s use first image from the list
size = sizes[0]  # same with the node size

# if you would like to have a ssh access to the Node - add auth parameter with your public_key
auth = NodeAuthSSHKey('ssh-rsa key here')

result = client.create_node(
    name="mynodetestnode",
    size=sizes[0],
    image=images[0],
    auth=auth
)
print(result)
nodes = client.list_nodes()
print(nodes)

# client.destroy_node(node=result)


```