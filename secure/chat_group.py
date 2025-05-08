S_ALONE = 0
S_TALKING = 1

# ==============================================================================
# Group class:
# member fields:
#   - An array of items, each a Member class
#   - A dictionary that keeps who is a chat group
# member functions:
#    - join: first time in
#    - leave: leave the system, and the group
#    - list_my_peers: who is in chatting with me?
#    - list_all: who is in the system, and the chat groups
#    - connect: connect to a peer in a chat group, and become part of the group
#    - disconnect: leave the chat group but stay in the system
# ==============================================================================

S_ALONE = 0
S_TALKING = 1

class Group:

    def __init__(self):
        self.members = {}
        self.chat_grps = {}
        self.grp_ever = 0

    def join(self, name):
        self.members[name] = S_ALONE
        return

    def is_member(self, name):

        # IMPLEMENTATION
        # ---- start your code ---- #
        if name in self.members.keys():
            return True

        return False
        # ---- end of your code --- #

    # implement
    def leave(self, name):
        """
        leave the system, and the group
        """
        # IMPLEMENTATION
        # ---- start your code ---- #
        del self.members[name]
        for key in list(self.chat_grps.keys()):
            if name in self.chat_grps[key]:
                self.chat_grps[key].remove(name)
                #to see if the group is only one person
                if len(self.chat_grps[key]) == 1:
                    del self.chat_grps[key]

        # ---- end of your code --- #
        return

    def find_group(self, name):
        """
        Auxiliary function internal to the class; return two
        variables: whether "name" is in a group, and if true
        the key to its group
        """

        found = False
        group_key = 0
        # IMPLEMENTATION
        # ---- start your code ---- #
        for i,j in self.chat_grps.items():
            if name in j:
                found = True
                group_key = i
                break

        # ---- end of your code --- #
        return found, group_key

    def connect(self, me, peer):
        """
        me is alone, connecting peer.
        if peer is in a group, join it
        otherwise, create a new group with you and your peer
        """
        peer_in_group, group_key = self.find_group(peer)

        # IMPLEMENTATION
        # ---- start your code ---- #
        if peer_in_group:
            self.chat_grps[group_key].append(me)
            self.members[me] = S_TALKING
        else:
            self.grp_ever += 1
            self.chat_grps[self.grp_ever] = [me, peer]
            self.members[me] = S_TALKING
            self.members[peer] = S_TALKING

        # ---- end of your code --- #
        return

    # implement
    def disconnect(self, me):
        """
        find myself in the group, quit, but stay in the system
        """
        # IMPLEMENTATION
        # ---- start your code ---- #
        peer_in_group, group_key = self.find_group(me)
        if peer_in_group:
            self.chat_grps[group_key].remove(me)
            self.members[me] = S_ALONE
            if len(self.chat_grps[group_key]) == 1:
                self.members[self.chat_grps[group_key][0]] = S_ALONE
                del self.chat_grps[group_key]

        # ---- end of your code --- #
        return

    def list_all(self):
        # a simple minded implementation
        full_list = "Users: ------------" + "\n"
        full_list += str(self.members) + "\n"
        full_list += "Groups: -----------" + "\n"
        full_list += str(self.chat_grps) + "\n"
        return full_list

    # implement
    def list_me(self, me):
        """
        return a list, "me" followed by other peers in my group
        """
        my_list = []
        # IMPLEMENTATION
        # ---- start your code ---- #
        for i in self.chat_grps.values():
            if me in i:
                my_list.append(me)
                for j in i:
                    if j != me:
                        my_list.append(j)

        # ---- end of your code --- #
        return my_list

    #how many loners are there in the system
    def count_loners(self):
        count = 0
        for status in self.members.values():
            if status == S_ALONE:
                count += 1
        return count
    
    #What is the biggest group?
    def biggest_group(self):
        max_size = 0
        biggest = None
        for group in self.chat_grps.values():
            if len(group) > max_size:
                max_size = len(group)
                biggest = group
        return biggest
    
    #list groups with a given length of members
    def list_groups_of_length(self, length):
        groups_of_length = []
        for group in self.chat_grps.values():
            if len(group) == length:
                groups_of_length.append(group)
        return groups_of_length

if __name__ == "__main__":
    g = Group()
    g.join('a')
    g.join('b')
    g.join('c')
    g.join('d')
    print(g.list_all())

    g.connect('a', 'b')
    print(g.list_all())
    g.connect('c', 'a')
    print(g.list_all())
    g.leave('c')
    print(g.list_all())
    g.disconnect('b')
    print(g.list_all())
