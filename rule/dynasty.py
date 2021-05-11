'''
TODO: 未完成（难，优先度低）
动态的validator set的生成机制
new validators to join and existing validators to leave
#first version: finished
#second version: deposit mechanism and first dynasty initialization finished
#third verison: transaction need to do
'''
import copy
import logging

logger = logging.getLogger(__name__)
from configuration.generalParameters import INIT_DYNASTY


class Dynasty:
    def __init__(self):
        # [(new,expert,retired)] d+2
        self.dynasties = [[[], INIT_DYNASTY, []], [[], [], []], [[], [], []]]
        self.current_epoch = 0  # d
        self.join_community = [] + INIT_DYNASTY
        # {validator_addr:[deposit,epoch]}
        self.deposit_bank = {}
        self.withdraw_delay = 1

    def joinDynasty(self, validator_address, deposit=1):
        '''
        func: apply to join the validator set
        args:
            validatorAddress: the identity of new validator
            deposit: the deposit of the new validator
        '''

        if not deposit or deposit <= 0:
            logger.warning('warning: validator %s please pay the deposit' % validator_address)
            return

        # 如果曾经加入过，就再也不能加入了
        if validator_address not in self.join_community:
            self.deposit_bank[validator_address] = [deposit, self.current_epoch]
            self.dynasties[self.current_epoch + 2][0].append(validator_address)
            # join
            self.join_community.append(validator_address)

    def quitDynasty(self, validator_address):
        '''
        func: apply to quit the validator set
        args:
            validatorAddress: the identity of new validator
        '''
        if validator_address in self.dynasties[self.current_epoch][1]:
            # join_dynasty changed to quit dynasty(d+2+5)
            self.deposit_bank[validator_address][1] = self.current_epoch + 2 + self.withdraw_delay
            self.dynasties[self.current_epoch + 2][2].append(validator_address)

        elif validator_address in self.dynasties[self.current_epoch + 1][0]:
            # join_dynasty changed to quit dynasty(d+2+5)
            self.deposit_bank[validator_address][1] = self.current_epoch + 2 + self.withdraw_delay
            self.dynasties[self.current_epoch + 2][0].remove(validator_address)
            self.dynasties[self.current_epoch + 2][2].append(validator_address)
        else:
            logger.warning('warning: %s not in the new and expert validator', str(validator_address))

    def dynastyChange(self):
        '''
        func: dynasty change
        '''
        self.current_epoch += 1

        self.dynasties.append([[], [], []])

        current_dynasty = self.dynasties[self.current_epoch]
        previous_dynasty = self.dynasties[self.current_epoch - 1]

        previous_new = set(copy.deepcopy(previous_dynasty[0]))
        previous_og = set(copy.deepcopy(previous_dynasty[1]))

        current_retire = set(copy.deepcopy(current_dynasty[2]))
        current_og = list(previous_og.union(previous_new) - current_retire)

        current_dynasty[1] = current_og
        #
        # self.dynasties.append(copy.deepcopy(self.dynasties[-1]))
        # # new validator move to expert validator
        # new_people = copy.deepcopy(self.dynasties[-1][0])
        # # print(self.dynasties[-1][1])
        # # print(new_people)
        # # self.dynasties[-1][1]=new_people
        # for validatorAddress in new_people:
        #     self.dynasties[-1][1].append(validatorAddress)
        # self.dynasties[-1][0].clear()
        # # print('current bank',self.deposit_bank)
        # removed_key = []
        # for k,v in self.deposit_bank.items():
        #     # print('-----------',k,v)
        #     if v[1] == self.current_epoch:
        #         removed_key.append(k)
        # if removed_key:
        #     for key in removed_key:
        #         self.deposit_bank.pop(key)
        #     removed_key = []
        #

# if __name__ == '__main__':
#     a = Dynasty()
#     #------join
#     a.join(1,10)
#     a.join(2,10)
#     a.join(3,0)
#     print('current dynasty ',a.current_epoch,'total dynasty',a.dynasties)
#     print('deposit bank ',a.deposit_bank)
#     #------dynastyChange
#     a.dynastyChange()
#     print('current dynasty ',a.current_epoch,'total dynasty',a.dynasties)
#     # #------
#     a.join(4,22)
#     print('current dynasty ',a.current_epoch,'total dynasty',a.dynasties)
#     print('deposit bank ', a.deposit_bank)
#     # #------wrong quit
#     a.quit(5)
#     print(a.dynasties)
#     # #------right quit
#     a.quit(1)
#     print('current dynasty ',a.current_epoch,'total dynasty',a.dynasties)
#     print('deposit bank ', a.deposit_bank)
#     # #------dynasty change
#     a.dynastyChange()
#     print('current dynasty ',a.current_epoch,'total dynasty',a.dynasties)
#     print('deposit bank ', a.deposit_bank)
#     a.dynastyChange()
#     print('current dynasty ', a.current_epoch, 'total dynasty', a.dynasties)
#     print('deposit bank ', a.deposit_bank)
#     a.dynastyChange()
#     print('current dynasty ', a.current_epoch, 'total dynasty', a.dynasties)
#     print('deposit bank ', a.deposit_bank)
#     print(a.join_community)
