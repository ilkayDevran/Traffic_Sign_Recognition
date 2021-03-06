# USAGE
# python pca.py -t ../ROI_images/training  
# python pca.py -t ../ROI_images/training -m m || -m s
# https://sebastianraschka.com/Articles/2014_pca_step_by_step.html

# import the necessary packages
from localbinarypatterns import LocalBinaryPatterns
from matplotlib import pyplot as plt
from imutils import paths
import numpy as np
import argparse
import cv2
import os
import pdb


# MANUAL VERSION
def compute_manually(all_samples, labels, samples_amount_of_classes,p=24,r=8, plot_it=False):

    histLength, sampleLength = all_samples.shape

    # Computing the d-dimensional mean vector
    mean_vector = []
    for i in all_samples:
        mean = np.mean(i)
        mean_vector.append([mean])

    mean_vector = np.array(mean_vector)
    #print mean_vector

    # Computing eigenvectors and corresponding eigenvalues
    eig_val_sc, eig_vec_sc , eig_val_cov, eig_vec_cov= None, None, None, None


    # Computing the Scatter Matrix
    scatter_matrix = np.zeros((histLength,histLength))
    for i in range(all_samples.shape[1]):
        scatter_matrix += (all_samples[:,i].reshape(histLength,1) - mean_vector).dot((all_samples[:,i].reshape(histLength,1) - mean_vector).T)
    eig_val_sc, eig_vec_sc = np.linalg.eig(scatter_matrix)

    # Computing the Covariance Matrix (alternatively to the scatter matrix)
    tmpList = []
    for i in all_samples:
        tmpList.append(i)
    cov_mat = np.cov(tmpList)
    eig_val_cov, eig_vec_cov = np.linalg.eig(cov_mat)

    for i in range(len(eig_val_sc)):
        eigvec_sc = eig_vec_sc[:,i].reshape(1,histLength).T
        eigvec_cov = eig_vec_cov[:,i].reshape(1,histLength).T
        assert eigvec_sc.all() == eigvec_cov.all(), 'Eigenvectors are not identical'
        """
        print('Eigenvector {}: \n{}'.format(i+1, eigvec_sc))
        print('Eigenvalue {} from scatter matrix: {}'.format(i+1, eig_val_sc[i]))
        print('Eigenvalue {} from covariance matrix: {}'.format(i+1, eig_val_cov[i]))
        print('Scaling factor: ', eig_val_sc[i]/eig_val_cov[i])
        print(40 * '-')
        """
    for i in range(len(eig_val_sc)):
        eigv = eig_vec_sc[:,i].reshape(1,histLength).T
        np.testing.assert_array_almost_equal(scatter_matrix.dot(eigv), eig_val_sc[i] * eigv,
            decimal=6, err_msg='', verbose=True)

    for ev in eig_vec_sc:
        np.testing.assert_array_almost_equal(1.0, np.linalg.norm(ev))

    # Make a list of (eigenvalue, eigenvector) tuples
    eig_pairs = [(np.abs(eig_val_sc[i]), eig_vec_sc[:,i]) for i in range(len(eig_val_sc))]

    # Sort the (eigenvalue, eigenvector) tuples from high to low
    eig_pairs.sort(key=lambda x: x[0], reverse=True)

    # Visually confirm that the list is correctly sorted by decreasing eigenvalues
    """for i in eig_pairs:
        print(i[0])
    """

    # Choosing k eigenvectors with the largest eigenvalues
    matrix_w = np.hstack((eig_pairs[0][1].reshape(histLength,1), eig_pairs[1][1].reshape(histLength,1)))
    #print('Matrix W:\n', matrix_w)

    # Transforming the samples onto the new subspace
    transformed = matrix_w.T.dot(all_samples)
    assert transformed.shape == (2,sampleLength), "The matrix is not 2x4527 dimensional."
   
    max_Y = 0.
    max_X = 0.
    min_Y = 0.
    min_X = 0.

    temp = 0
    for i,val in enumerate(samples_amount_of_classes):
        #raw_input("Class name: {}".format(labels[i]))
        max_X, min_X, max_Y, min_Y = find_max_min_X_Y(transformed[0,temp:val+temp],transformed[1,temp:val+temp],
            max_X, min_X, max_Y, min_Y)
        plt.plot(transformed[0,temp:val+temp], transformed[1,temp:val+temp],
         'o', markersize=7, color=np.random.rand(3,), alpha=0.5, label=labels[i])
        #plt.show()
        temp = val
    plt.xlim([min_X,max_X])
    plt.ylim([min_Y, max_Y])
    plt.xlabel('x_values')
    plt.ylabel('y_values')
    #plt.legend()
    plt.title('-Manual- Points: '+ str(p) + " Radius:" + str(r))

    if plot_it == False:
        fname = '/Users/ilkay/Desktop/figures/manual/m_' + str(p) +"_" + str(r) + ".svg"
        plt.savefig(fname, format='svg')
    else:
        plt.show()

    print '-Manual- Points: '+ str(p) + ' Radius:' + str(r) + ' DONE!'

# SKLEARN VERSION
def use_sklearn(all_samples, labels, samples_amount_of_classes,p=24,r=8, plot_it=False):
    from sklearn.decomposition import PCA as sklearnPCA

    sklearn_pca = sklearnPCA(n_components=2)
    sklearn_transf = sklearn_pca.fit_transform(all_samples.T)
    sklearn_transf = sklearn_transf.T

    max_Y = 0.
    max_X = 0.
    min_Y = 0.
    min_X = 0.

    temp = 0
    for i,val in enumerate(samples_amount_of_classes):

        max_X, min_X, max_Y, min_Y = find_max_min_X_Y(sklearn_transf[0,temp:val+temp],sklearn_transf[1,temp:val+temp],
            max_X, min_X, max_Y, min_Y)
        plt.plot(sklearn_transf[0,temp:val+temp],sklearn_transf[1,temp:val+temp], 'o', markersize=7, color=np.random.rand(3,), alpha=0.5, label=labels[i])
        temp = val
        # plt.show()
        # raw_input("Class name: {}".format(labels[i]))

    plt.xlabel('x_values')
    plt.ylabel('y_values')
    plt.xlim([min_X,max_X])
    plt.ylim([min_Y, max_Y])
    #plt.legend()
    plt.title('-SKleanr- Points: '+ str(p) + " Radius:" + str(r))
    if plot_it == False:
        fname = '/Users/ilkay/Desktop/figures/sklearn/s_' + str(p) +"_" + str(r) + ".svg"
        plt.savefig(fname, format='svg')
    else:
        plt.show()
    print '-SKleanr- Points: '+ str(p) + ' Radius:' + str(r) + ' DONE!'


# Find max min X and Y for plotting
def find_max_min_X_Y(x, y, max_X, min_X, max_Y, min_Y):
    
    max_of_x_list = max(x)
    min_of_x_list = min(x)
    max_of_y_list = max(y)
    min_of_y_list = min(y)

    if max_of_x_list > max_X:
        max_X = max_of_x_list
    elif min_of_x_list < min_X :
        min_X = min_of_x_list

    if max_of_y_list > max_Y:
        max_Y = max_of_y_list
    elif min_of_y_list < min_Y :
        min_Y = min_of_y_list

    return (max_X, min_X, max_Y, min_Y)


# GET LBP FEATURES 
def get_all_samples(path, p=24, r=8 ):
    # initialize the local binary patterns descriptor along with the data and label lists
    desc = LocalBinaryPatterns(p, r)
    data = []
    labels = []
    classSamplesList = []
    samples_amount_of_classes = []
    currentClass = None
    flag = False

    class_list = os.listdir(path)
    class_list.remove('.DS_Store')
    class_list.remove('Readme.txt')
    counter = len(class_list)

    lastClassPath = ''
    # loop over the training images
    for imagePath in paths.list_files(path, validExts=(".png",".ppm")):
        if (flag == False):
            currentClass = imagePath.split("/")[-2]
            labels.append(currentClass)
            counter -= 1
            flag = True
        else:
            if imagePath.split("/")[-2] != currentClass:
                currentClass = imagePath.split("/")[-2]
                classSamplesList.append(np.transpose(np.array(data)))
                samples_amount_of_classes.append(len(data))
                data = []
                labels.append(currentClass)
                counter -= 1
        if counter == 0:
            lastClassPath = imagePath
            break
                	
        # load the image, convert it to grayscale, and describe it
        image = cv2.imread(imagePath)
        gray = np.matrix(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
        resized_image = cv2.resize(gray, (32, 32))
        hist = desc.describe(resized_image)
        hist = hist / max(hist)
        
        # extract the label from the image path
        data.append(hist)

    data = []
    head, _ = os.path.split(lastClassPath)

    for imagePath in paths.list_files(head, validExts=(".png", ".ppm")):
        # load the image, convert it to grayscale, and describe it
        image = cv2.imread(imagePath)
        gray = np.matrix(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
        resized_image = cv2.resize(gray, (32, 32))
        hist = desc.describe(resized_image)
        hist = hist / max(hist)
	    # extract the label from the image path
        data.append(hist)

    classSamplesList.append(np.transpose(np.array(data)))
    samples_amount_of_classes.append(len(data))


    all_samples =  tuple(classSamplesList)
    all_samples = np.concatenate(all_samples, axis=1)

    """
    for i, val in enumerate(samples_amount_of_classes):
        print i, val
    raw_input()
    """
    return all_samples, labels ,samples_amount_of_classes


# MAIN
if __name__ == '__main__':
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--training", required=True,
        help="path to the training images")
    ap.add_argument("-m", "--Mod", type = str, default = 'man',
        help="Calculate Manually")
    ap.add_argument("-mat", "--matplot", type = str, default = '',
        help="Calculate with Matplotlib")
    ap.add_argument("-s", "--sklearn", type = str, default = '',
        help="Calculate with Sklearn")
    args = vars(ap.parse_args())


    # get all_samples list
    all_samples, labels, samples_amount_of_classes = get_all_samples(args["training"])

    # choose calculation mod 
    calculationMod = args["Mod"]
    if calculationMod == 's' or calculationMod == 'sklearn':
        use_sklearn(all_samples, labels, samples_amount_of_classes,plot_it=True)
    elif calculationMod == 't' or calculationMod == 'test':
        radiuses = [2,4,8,16,32]
        points = [2,4,6,8,16,32,64,128,256]
        total = str(len(radiuses)*len(points))
        print "Total = " + total
        counter = 0
        for r in radiuses:
            for p in points:
                print "\n Remaining --> " + str(counter) + "/" + total 
                counter += 1
                all_samples, labels, samples_amount_of_classes = get_all_samples(args["training"],
                    p=p,r=r)
                compute_manually(all_samples, labels, samples_amount_of_classes,p,r)
                use_sklearn(all_samples, labels, samples_amount_of_classes,p,r)
    else:
        compute_manually(all_samples, labels, samples_amount_of_classes, plot_it=True)