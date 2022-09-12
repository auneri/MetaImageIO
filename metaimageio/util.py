import numpy as np


def get_transform(meta):
    translation = np.eye(4)
    if int('Position' in meta) + int('Offset' in meta) + int('Origin' in meta) > 1:
        raise ValueError('Ambigious definition of position')
    if 'Position' in meta:
        translation[:3,3] = meta['Position']
    elif 'Offset' in meta:
        translation[:3,3] = meta['Offset']
    elif 'Origin' in meta:
        translation[:3,3] = meta['Origin']
    rotation = np.eye(4)
    if int('Orientation' in meta) + int('Rotation' in meta) + int('TransformMatrix' in meta) > 1:
        raise ValueError('Ambigious definition of orientation')
    if 'Orientation' in meta:
        rotation[:3,:3] = meta['Orientation']
    elif 'Rotation' in meta:
        rotation[:3,:3] = meta['Rotation']
    elif 'TransformMatrix' in meta:
        rotation[:3,:3] = meta['TransformMatrix']
    center_of_rotation = np.eye(4)
    if 'CenterOfRotation' in meta:
        center_of_rotation[:3,3] = meta['CenterOfRotation']
    return translation.dot(center_of_rotation).dot(rotation).dot(np.linalg.inv(center_of_rotation))


def set_transform(meta, transform, position_key='Position', orientation_key='Orientation'):
    if any(i in meta for i in ('Position', 'Offset', 'Origin')):
        raise ValueError('Position is already defined in meta')
    if any(i in meta for i in ('Orientation', 'Rotation', 'TransformMatrix')):
        raise ValueError('Orientation is already defined in meta')
    meta[position_key] = transform[:3,3]
    meta[orientation_key] = transform[:3,:3]
    meta['CenterOfRotation'] = np.zeros(3)
    return meta
