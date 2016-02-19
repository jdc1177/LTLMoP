import pymatlab
import numpy as np
import logging
import platform
from collections import OrderedDict
from math import sin, cos

threshold = 10
robRadius = OrderedDict([('rob2',0.15), ('rob1',0.15)])
robMaxVel = OrderedDict([('rob2',0.5), ('rob1',0.5)])
# regionNumbers = OrderedDict([('p9',1),('p7',2),('p5',3),('p6',4),('p8',5)])  # Hack: Temporarily hard-coding TODO: bring in from the region file.
robots = [robRadius, robMaxVel]

system = platform.system()
pathToMatlabLocalPlanner = '/home/jon/Dropbox/Research/LowLevelControllerSynthesis/reasyns/scripts'

def initializeController(session, regions, scalingPixelsToMeters, limitsMap):
    """
    intialize Local Planner by setting up a pymatlab session and setting variables
    """
    logging.info('Starting Matlab session...')
    # session = pymatlab.session_factory()

    # Initialize the local planner
    session.run('cd '+pathToMatlabLocalPlanner)

    session.run('initExecute();')
    print str(session.getvalue('errorMsg'))

    v,w,acLastData = executeControllersSingleStep(aut,sys,ac_trans,ac_inward,pose,id_region_1,id_region_2,acLastData)
    print str(session.getvalue('errorMsg'))

    # session.putvalue('rRob',robotRadius)
    # logging.debug("  rRob (matlab): "+str(session.getvalue('rRob')))

    session.putvalue('limitsMap',limitsMap)
    logging.debug("  limitsMap (matlab): "+str(session.getvalue('limitsMap')))

    
    # return matlab session
    # return session

def executeController(session, poseDic, regions, curr, next, coordmap_lab2map, scalingPixelsToMeters, doUpdate):
    """
    pose  = {'rob1':[-1 ,.5],'rob2':[1,1],'rob3':[3.5 , -1]}
    next_regIndices = {'rob1': 2,'rob2':3,'rob3':3}
    """

    numRobots = len(poseDic)

    for i, poseLoc in enumerate(poseDic.iteritems()):
        roboName = poseLoc[0]

        # Set the current pose: PYTHON: pose, MATLAB: zAux  (size d x n)  
        # poseNew = np.float_(np.hstack([float(1)/scalingPixelsToMeters*np.array(coordmap_lab2map(poseLoc[1][0:2])), poseLoc[1][2]]))
        pose = np.float_(np.hstack([float(1)/scalingPixelsToMeters*poseLoc[1][0:2], poseLoc[1][2]]))
        # poseNew = np.float_(poseLoc[1])
        session.putvalue('pose',pose)
        logging.debug("  pose (matlab): "+str(session.getvalue('pose')))
        # print("  pose (matlab): "+str(session.getvalue('pose')))

        if doUpdate[roboName]:

            currRegName = regions[curr[roboName]].name
            nextRegName = regions[next[roboName]].name
            print "current region: "+currRegName
            print "next region: "+nextRegName
            # print regionNumbers
            currNbr = [[]]; nextNbr =[[]]
            for currRegNbr, region in enumerate(regions):
                if region.name == regions[curr[roboName]].name:
                    break
            for nextRegNbr, region in enumerate(regions):
                if region.name == regions[next[roboName]].name:
                    break
            # print currRegNbr, nextRegNbr
            currNbr[0] = currRegNbr+1; nextNbr[0] = nextRegNbr+1
            # currRegNbr[0] = regions.name.index(currRegName) #regionNumbers[currRegName]
            # nextRegNbr[0] = regionNumbers[nextRegName]
            session.putvalue('id_region_1',np.float_(currNbr))
            session.putvalue('id_region_2',np.float_(nextNbr))
            session.run('currentNextRegions('+str(i+1)+',:) = [id_region_1, id_region_2];')

            logging.debug("  id_region_1 (matlab): "+str(session.getvalue('id_region_1')))
            logging.debug("  id_region_2 (matlab): "+str(session.getvalue('id_region_2')))
            print "  id_region_1 (matlab): "+str(session.getvalue('id_region_1'))
            print "  id_region_2 (matlab): "+str(session.getvalue('id_region_2'))


    # Execute one step of the local planner and collect velocity components
    try:
        v,w,acLastData = executeControllersSingleStep(aut,sys,ac_trans,ac_inward,pose,id_region_1,id_region_2,acLastData)
    except:
        print "WARNING: Matlab execute function experienced an error!!"

    # print str(session.getvalue('errorMsg'))
    v = {}
    w = {}
    for i, poseLoc in enumerate(poseDic.iteritems()):
        # logging.debug('v = ' + str(session.getvalue('vOut'+str(i+1))))
        # logging.debug('w = ' + str(session.getvalue('wOut'+str(i+1))))

        v[i] = 1*scalingPixelsToMeters*session.getvalue('v')
        w[i] = 1*session.getvalue('w') #0.25*session.getvalue('wOut'+str(i+1))
        # deadAgent.append(session.getvalue('deadlockAgent'+str(i+1)))
        # print "Deadlock status (agent "+str(i)+") :"+str(deadAgent[i])


    # return velocities
    return v, w

def initializeController():


def executeControllersSingleStep(aut,sys,ac_trans,ac_inward,pose,id_region_1,id_region_2,acLastData):

    persistent t_offset t_base tend ell t_trials

    global u_sav x_sav x0_sav

    delayTime = -0.1

    timeBaseFlag = false  # if 'true', use time as a basis for choosing the TVLQR states; otherwise use a weighted Euclidean distance.
    useLastAC = true

    #################
    # Account for our manual shifting of the map to the left because of the "dead zone" in the Vicon field 
    x(1) = x(1) + 0.0043
    x(2) = x(2) + 0.1629
    #################

    #################
    # Account for our manual shifting of the map
    x(1) = x(1) - 0.9774
    x(2) = x(2) + 0.0258
    #################

    x(3) = x(3) + 0.2  # theta bias needed to account for misalignment of the youBot's coordinate frame wrt. its true orientation

    prevCtrl = false

    if isempty(t_base):
        t_base = clock

    vx = 0
    vy = 0
    w = 0.001
    errorMsg = 'nothing to see here...'

    teval = 0.02;

    # flip! if necessary
    #if size(x,2) > size(x,1):
    #    x = x'
    
    trans = vertcat(aut.trans{:});
    currStateVec = find([aut.q{:}]==currReg);
    nextStateVec = find([aut.q{:}]==nextReg);
    currTrans = find(ismember(trans(:,1),currStateVec) & ismember(trans(:,2),nextStateVec), 1);
    if isempty(currTrans):
        error('you have specified an invalid transition!')
    currState = trans(currTrans,1);  nextState = trans(currTrans,2)
    
    # deal with the possibility of sys being a cell array of systems.
    if length(sysArray) > 1:
        sys = sysArray(aut.f{currTrans})
    else:
        sys = sysArray
    
    # identify the funnel we're in and get the ellipse index
    iTrans = false
    iIn = false
    if isinternal(ac_trans{currTrans}, x,'u',sys):
    # if isinternal(ac_trans{currTrans}, x,'u')
        iTrans = currTrans
        ac = ac_trans{currTrans}
    if iTrans == false && ~isempty(ac_inward):
        for funIdx = 1:length(ac_inward{currState})
            if isinternal(ac_inward{currState}(funIdx), x,'u',sys)
                #         if isinternal(ac_inward{currState}, x,'u')
                iIn = currState
                ac = ac_inward{currState}(funIdx)
    
    # if no funnels in the new region/transition OR have temporarily left a funnel, then keep activating the previous one.
    currStateOld = []
    nextStateOld = []
    if ~iTrans && ~iIn:
        if useLastAC:
            # propagate the appropriate old states on to the next iteration
            if ~isempty(acLastData{5}) && ~isempty(acLastData{6}):
                currStateOld = acLastData{5};  nextStateOld = acLastData{6}
            else:
                currStateOld = acLastData{3};  nextStateOld = acLastData{4}

            currTransOld = ( trans(:,1) == currStateOld & trans(:,2) == nextStateOld )
            if ~isempty(acLastData{1}):
                ac = ac_trans{currTransOld}
            else:
                ac = ac_inward{currStateOld}
            iTrans = acLastData{1}
            iIn = acLastData{2}
            prevCtrl = true
            print('WARNING: no funnels found! Using the previous controller.')
        else
            iTrans = currTrans
            ac = ac_trans{currTrans}
            print('WARNING: no funnels found! Forcing an (unverified) controller.')
    
    # determine the new time offset if something has changed
    if timeBaseFlag:
        acData = {iTrans, iIn, currState, nextState, currStateOld, nextStateOld};
        for i in range(len(acData)-2):
            cmp(i) = acData{i}==acLastData{i}
        end
        cmp
        if (~all(cmp) || ~(all(ismember([acLastData{1:4}],[acData{1:4}])) && all([acLastData{3:4}] == [acData{3:4}]))) && ~prevCtrl
            t_trials = getTimeVec(ac.x0)
            tend = t_trials(end)
            t_base = clock
            ell = ellipsoid(ac)
            
            for i = 1:length(ell)
                if isinternal(ell(i),x,'u')
                    t_offset = t_trials(i)
                    break

        acLastData = acData
        
        if isempty(t):  # if time is not given, we compute it here
            t = etime(clock,t_base) + delayTime
        t_offset
        teval = min(tend,t + t_offset)

    else:
        acData = {iTrans, iIn, currState, nextState, currStateOld, nextStateOld}
        for i = 1:length(acData)-2:
            cmp(i) = acData{i}==acLastData{i}
        if ~all(cmp) || ~(all(ismember([acLastData{1:4}],[acData{1:4}])) && all([acLastData{3:4}] == [acData{3:4}])):
            t_base = clock
            ell = ellipsoid(ac)
            t_trials = getTimeVec(ac.x0)

        acLastData = acData
        
        minDelta = inf;
        weights = [1;1;0.2]
        for i = 2:3:length(ell)
            xtmp = double(ac.x0, t_trials(i));
            testMinDist = min([
                norm(weights.*(xtmp(1:3) - (x(1:3)+[0 0 2*pi]))) 
                norm(weights.*(xtmp(1:3) - x(1:3))) 
                norm(weights.*(xtmp(1:3) - (x(1:3)-[0 0 2*pi])))])
            if testMinDist < minDelta
                teval = t_trials(i)
                minDelta = testMinDist
        if isempty(t)  # if time is not given, we compute it here
            t = etime(clock,t_base)
    
    # compute a command
    teval
    K = double(ac.K,teval)
    x0 = double(ac.x0,teval)
    u0 = double(ac.u0,teval)
    
    K = K(end-length(u0)+1:end,:)
    
    u_test = [(K*(x+[0 0 2*pi] - x0)) (K*(x - x0)) (K*(x-[0 0 2*pi] - x0))]
    u_idx = abs(u_test(end,:)) == min(abs(u_test(end,:)))
    u_ctrl = u_test(:,u_idx)
    u = u0 + 1*u_ctrl(:,1)
    # u(2) = max(min(u(2),16),-16);
    
    if aut.f{currTrans} == 1:  # we're using diff-drive dynamics
        vx = u(1);  w = max(min(u(2),0.2),-0.2);
    else if aut.f{currTrans} == 2:  # we're using holonomic-drive dynamics
        u_local = [cos(-x(3)) -sin(-x(3));sin(-x(3)) cos(-x(3))]*u(1:2)
        vx = 1*u_local(1);  vy = 1*u_local(2);  w = u(3);
    else:
        error('unhandled system identifier!')
    
    #u_sav = [u_sav; t u]
    x_sav = [x_sav; t x]
    x0_sav = [x0_sav; t x0]

    return v,w,acLastData