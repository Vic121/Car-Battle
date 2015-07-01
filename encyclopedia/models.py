# import logging
# from django.core.cache import cache

# class FriendManager(models.Manager):
# 	pass
# 
# class Friend(models.Model):
# 	user = models.ForeignKey(User, related_name='user')
# 	friend = models.ForeignKey(User, related_name='friend')
# 	is_accepted = models.BooleanField(default=False)
# 	
# 	objects = FriendManager()
# 	
# 	class Meta:
# 		db_table = 'user_friend'
# 		verbose_name = 'Friend'
# 
# 	def __unicode__(self):
# 		return '%s friend of %s' % (self.user, self.friend)
