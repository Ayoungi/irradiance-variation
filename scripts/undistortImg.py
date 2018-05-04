import numpy as np
from scipy import interpolate
import scripts.internal_calibration

def undistortCC(img, sizeResult = [500, 500, 3] , altitude = 150 , rot = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]) , trans = np.array([[0], [0], [0]]) , bearing = 0 , elevation = 0 , pixelWidth=1, cuda=False):
    """Undistort a fish-eye image to a standard camera image by a ray-tracing approach.
    img: the fish-eye image to undistort
    sizeResult: the size of the output undistorted image [pixels]
    altitude: the altitude of the virtual image plane to form the undistorted image [meters]
    rot: a rotation matrix (3x3) to cope with the misalignement of the image
    trans: a translation matrix (3x1) to cope with the misalignement of the image
    bearing: the bearing angle of the undistorted plane (in degrees)
    elevation: the elevation angle of the undistorted plane (in degrees)
    pixelWidth: the width in real world coordinates of one pixel of the undistorted image [meters]
    cuda: set to True if cuda (GPU) interpolation is used
    """

    centerImage = np.array([sizeResult[1]/2, sizeResult[0]/2])
    
    if len(np.shape(img)) == 3:
        R = img[:,:,0]
        G = img[:,:,1]
        B = img[:,:,2]
    
    sizeImg = img.shape
    posX, posY = np.meshgrid(np.arange(sizeImg[1]), np.arange(sizeImg[0]))
    posX = posX + 1
    posY = posY + 1

    mapY, mapX = np.meshgrid(np.arange(sizeResult[1]), np.arange(sizeResult[0]))
    mapX = mapX + 1
    mapY = mapY + 1
    distCenterX = (mapX.ravel(order='F') - centerImage[0]) * pixelWidth
    distCenterY = (mapY.ravel(order='F') - centerImage[1]) * pixelWidth
    distCenterZ = np.tile(-altitude, (distCenterX.shape[0], 1))
    
    bearing = np.radians(bearing)
    elevation = np.radians(elevation)
    rotHg = np.array([[np.cos(elevation), 0, np.sin(elevation)], [0, 1, 0], [-np.sin(elevation), 0, np.cos(elevation)]])
    rotBearing = np.array([[np.cos(bearing), -np.sin(bearing), 0], [np.sin(bearing), np.cos(bearing), 0], [0, 0, 1]])
    
    worldCoords = np.column_stack((distCenterX, distCenterY, distCenterZ)).T
    
    worldCoords = np.dot(rotHg, worldCoords)
    worldCoords = np.dot(rotBearing, worldCoords)
    worldCoords = np.dot(rot.T, worldCoords - trans)
    
    m = scripts.internal_calibration.world2cam(worldCoords)

    if len(np.shape(img)) == 3:
        if cuda:
            result = cuda_interpolate3D(img, m, (sizeResult[0], sizeResult[1]))
        else:
            ip = interpolate.RectBivariateSpline(np.arange(sizeImg[0]), np.arange(sizeImg[1]), R)
            resultR = ip.ev(m[0,:]-1, m[1,:]-1)
            resultR = resultR.reshape(sizeResult[0], sizeResult[1],order='F')
            np.clip(resultR, 0, 255, out=resultR)
            resultR = resultR.astype('uint8')

            ip = interpolate.RectBivariateSpline(np.arange(sizeImg[0]), np.arange(sizeImg[1]), G)
            resultG = ip.ev(m[0,:]-1, m[1,:]-1)
            resultG = resultG.reshape(sizeResult[0], sizeResult[1],order='F')
            np.clip(resultG, 0, 255, out=resultG)
            resultG = resultG.astype('uint8')

            ip = interpolate.RectBivariateSpline(np.arange(sizeImg[0]), np.arange(sizeImg[1]), B)
            resultB = ip.ev(m[0,:]-1, m[1,:]-1)
            resultB = resultB.reshape(sizeResult[0], sizeResult[1],order='F')
            np.clip(resultB, 0, 255, out=resultB)
            resultB = resultB.astype('uint8')

            result = np.zeros(sizeResult).astype('uint8')
            result[:,:,0] = resultR
            result[:,:,1] = resultG
            result[:,:,2] = resultB
    else:
        if cuda:
            result = cuda_interpolate(img, m, (sizeResult[0], sizeResult[1]))
        else:
            ip = interpolate.RectBivariateSpline(np.arange(sizeImg[0]), np.arange(sizeImg[1]), img)
            result = ip.ev(m[0,:]-1, m[1,:]-1)
            result = result.reshape(sizeResult[0], sizeResult[1],order='F')
            np.clip(result, 0, 255, out=result)
            result = result.astype('uint8')
    
    return result





