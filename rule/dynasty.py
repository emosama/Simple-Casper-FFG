'''
TODO: 未完成（难，优先度低）
动态的validator set的生成机制
new validators to join and existing validators to leave
#first version: finished
#second version: deposit mechanism and first dynasty initialization
'''
import copy
import logging
logger = logging.getLogger(__name__)

class Dynasty:
    def __init__(self):
        # [(new,expert,retired)] d+2
        self.dynasties = [([],[],[]),([],[],[]),([],[],[])]
        self.current_epoch = 1 #d
        self.join_community = set()

    def join(self,validatorAddress):
        '''
        func: apply to join the validator set
        args:
            validatorAddress: the identity of new validator
        '''
        if validatorAddress not in self.join_community:
            self.dynasties[self.current_epoch+1][0].append(validatorAddress)
            #join
            self.join_community.add(validatorAddress)
    def quit(self,validatorAddress):
        '''
        func: apply to quit the validator set
        args:
            validatorAddress: the identity of new validator
        '''
        if validatorAddress in self.dynasties[self.current_epoch+1][0] or \
                validatorAddress in self.dynasties[self.current_epoch+1][1]:
            self.dynasties[self.current_epoch+1][2].append(validatorAddress)
            self.dynasties[self.current_epoch+1][1].remove(validatorAddress)
        else:
            logger.warning('warning: %s not in the expert validator',str(validatorAddress))
            # print('wrong')
    def dynastyChange(self):
        '''
        func: dynasty change
        '''
        self.current_epoch += 1
        self.dynasties.append(copy.deepcopy(self.dynasties[-1]))
        # new validator move to expert validator
        new_people = copy.deepcopy(self.dynasties[-1][0])
        self.dynasties[-1][1].extend(new_people)
        self.dynasties[-1][0].clear()
        # if self.dynasties[-1][2]:
        #     quit_validator = copy.deepcopy(self.dynasties[-1][2])
        #     for qv in quit_validator:
        #         self.join_community.add(qv)
            # print('-----',self.retired_community)
            # self.dynasties[-1][2].clear()

if __name__ == '__main__':
    a = Dynasty()
    #------join
    a.join(1)
    a.join(2)
    a.join(3)
    print('current dynasty ',a.current_epoch,'total dynasty',a.dynasties)
    #------dynastyChange
    a.dynastyChange()
    print('current dynasty ',a.current_epoch,'total dynasty',a.dynasties)
    #------
    a.join(4)
    print('current dynasty ',a.current_epoch,'total dynasty',a.dynasties)
    #------wrong quit
    # a.quit(4)
    # print(a.dynasties)
    #------right quit
    a.quit(1)
    print('current dynasty ',a.current_epoch,'total dynasty',a.dynasties)
    #------dynasty change
    a.dynastyChange()
    print('current dynasty ',a.current_epoch,'total dynasty',a.dynasties)
    print(a.join_community)