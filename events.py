import sys
sys.path.append('C:\\Projeter\\farligfarligslange\\events')
from FullEvent import *
import random

class MoveCard(Event):
	name = 'MoveCard'
	def setup(self, **kwargs):
		self.i = self.frm.index(self.card)
		if self.i==None: return True
	def payload(self, **kwargs):
		self.card = self.frm.pop(self.i)
		self.to.append(self.card)
		return self.card
		
class GainOwnership(Event):
	name = 'GainOwnership'
	def payload(self, **kwargs):
		self.card.setOwner(self.player)
		self.player.owns.append(self.card)
		
class LooseOwnership(Event):
	name = 'LooseOwnership'
	def payload(self, **kwargs):
		self.card.owner.owns.remove(self.card)
		self.card.setOwner(None)
		
class Gain(Event):
	name = 'Gain'
	def setup(self, **kwargs):
		if not hasattr(self, 'to'): self.to = self.player.discardPile
		self.gainedCard = self.spawnTree(MoveCard).resolve()
		if not self.gainedCard: return True
	def payload(self, **kwargs):
		self.spawn(GainOwnership).resolve()
		return self.gainedCard
		
class GainFromPile(Event):
	name = 'GainFromPile'
	def setup(self, **kwargs):
		self.card = self.frm.viewTop()
		if not self.card: return True
	def payload(self, **kwargs):
		return self.spawnTree(Gain).resolve()
		
class Take(Event):
	name = 'Take'
	def setup(self, **kwargs):
		if not hasattr(self, 'to'): self.to = self.player.discardPile
		self.gainedCard = self.spawnTree(MoveCard).resolve()
		if not self.gainedCard: return True
	def payload(self, **kwargs):
		self.spawn(GainOwnership).resolve()
		return self.gainedCard
		
class TakeFromPile(Event):
	name = 'TakeFromPile'
	def setup(self, **kwargs):
		self.card = self.frm.viewTop()
		if not self.card: return True
	def payload(self, **kwargs):
		return self.spawnTree(Take).resolve()
		
class Discard(Event):
	name = 'Discard'
	def setup(self, **kwargs):
		if not hasattr(self, 'frm'): self.frm = self.player.hand
		if not hasattr(self, 'to'): self.to = self.player.discardPile
		self.discardedCard = self.spawnTree(MoveCard).resolve()
		if not self.discardedCard: return True
	def payload(self, **kwargs):
		return self.discardedCard
		
class Destroy(Event):
	name = 'Destroy'
	def setup(self, **kwargs):
		if not hasattr(self, 'frm'): self.frm = self.player.inPlay
		if not hasattr(self, 'to'): self.to = self.player.discardPile
		self.destroyedCard = self.spawnTree(MoveCard).resolve()
		if not self.destroyedCard: return True
	def payload(self, **kwargs):
		return self.destroyedCard
		
class Trash(Event):
	name = 'Trash'
	def setup(self, **kwargs):
		if not hasattr(self, 'to'): self.to = self.session.trash
		self.trashedCard = self.spawnTree(MoveCard).resolve()
		if not self.trashedCard: return True
	def payload(self, **kwargs):
		self.spawn(LooseOwnership).resolve()
		return self.trashedCard
		
class ReturnCard(Event):
	name = 'ReturnCard'
	def setup(self, **kwargs):
		name = self.card.printedValues.name
		if not hasattr(self, 'to'):
			if name in self.session.piles: self.to = self.session.piles[name]
			elif name in self.session.NSPiles: self.to = self.session.NSPiles[name]
		self.returnedCard = self.spawnTree(MoveCard).resolve()
		if not self.returnedCard: return True
	def payload(self, **kwargs):
		self.spawn(LooseOwnership).resolve()
		return self.returnedCard
		
class ResolveCard(Event):
	name = 'ResolveCard'
	def payload(self, **kwargs):
		self.card.onPlay(self.player)
		self.session.resolveTriggerQueue()
		
class PlayCard(Event):
	name = 'PlayCard'
	def payload(self, **kwargs):
		self.spawnTree(ResolveCard).resolve()
		
class CastCard(Event):
	name = 'CastCard'
	def setup(self, **kwargs):
		if not hasattr(self, 'frm'): self.frm = self.player.hand
		if not hasattr(self, 'to'): self.to = self.player.inPlay
	def payload(self, **kwargs):
		card = self.spawnTree(MoveCard).resolve()
		if not card: return
		self.spawnTree(PlayCard).resolve()
		return True
		
class AddCoin(Event):
	name = 'AddCoin'
	def setup(self, **kwargs):
		if not hasattr(self, 'amnt'): self.amnt = 1
		if self.amnt==0: return True
	def payload(self, **kwargs):
		if self.amnt<1: return
		amn = self.amnt
		if self.player.minusCoin:
			amn -= 1
			self.player.minusCoin = False
		self.player.coins += amn
		
class AddPotion(Event):
	name = 'AddPotion'
	def setup(self, **kwargs):
		if not hasattr(self, 'amnt'): self.amnt = 1
		if self.amnt==0: return True
	def payload(self, **kwargs):
		if self.amnt<1: return
		self.player.potions += self.amnt
		
class AddDebt(Event):
	name = 'AddDebt'
	def setup(self, **kwargs):
		if not hasattr(self, 'amnt'): self.amnt = 1
		if self.amnt==0: return True
	def payload(self, **kwargs):
		if self.amnt<1: return
		self.player.debt += self.amnt

class AddAction(Event):
	name = 'AddAction'
	def setup(self, **kwargs):
		if not hasattr(self, 'amnt'): self.amnt = 1
		if self.amnt==0: return True
	def payload(self, **kwargs):
		if self.amnt<1: return
		self.player.actions += self.amnt

class AddBuy(Event):
	name = 'AddBuy'
	def setup(self, **kwargs):
		if not hasattr(self, 'amnt'): self.amnt = 1
		if self.amnt==0: return True
	def payload(self, **kwargs):
		if self.amnt<1: return
		self.player.buys += self.amnt
		
class AddVictory(Event):
	name = 'AddVictory'
	def setup(self, **kwargs):
		if not hasattr(self, 'amnt'): self.amnt = 1
		if self.amnt==0: return True
	def payload(self, **kwargs):
		if self.amnt<1: return
		self.player.victories += self.amnt
		
class Reshuffle(Event):
	name = 'Reshuffle'
	def payload(self, **kwargs):
		while self.player.discardPile: self.player.library.append(self.player.discardPile.pop())
		random.shuffle(self.player.library)
		
class RequestCard(Event):
	name = 'RequestCard'
	def payload(self, **kwargs):
		if not self.player.library:
			self.spawnTree(Reshuffle).resolve()
			if not self.player.library: return
		return self.player.library[-1]
		
class RequestCards(Event):
	name = 'RequestCards'
	def setup(self, **kwargs):
		if not hasattr(self, 'amnt'): self.amnt = 1
	def payload(self, **kwargs):
		if len(self.player.library)<self.amnt:
			self.spawnTree(Reshuffle).resolve()
		if not self.player.library: return []
		return self.player.library[-np.min((self.amnt, len(self.player.library))):]
	
class Draw(Event):
	name = 'Draw'
	def setup(self, **kwargs):
		self.frm = self.player.library
		self.to = self.player.hand
		self.card = self.spawnTree(RequestCard).resolve()
		if not self.card: return True
	def payload(self, **kwargs):
		return self.spawnTree(MoveCard).resolve()
			
class DrawCards(Event):
	name = 'DrawCards'
	def setup(self, **kwargs):
		if not hasattr(self, 'amnt'): self.amnt = 1
	def payload(self, **kwargs):
		for i in range(self.amnt):
			if not self.spawnTree(Draw).resolve(): break
		
class CanPay(Event):
	name = 'CanPay'
	def payload(self, **kwargs):
		if self.player.buys<1 or self.player.coins<self.card.coinPrice.access() or self.player.potions<self.card.potionPrice.access() or self.player.debt>0: return False
		else: return True
		
class Pay(Event):
	name = 'Pay'
	def payload(self, **kwargs):
		if self.player.buys<1 or self.player.coins<self.card.coinPrice.access() or self.player.potions<self.card.potionPrice.access() or self.player.debt>0: return False
		self.player.buys -= 1
		self.player.coins -= self.card.coinPrice.access()
		self.player.potions -= self.card.potionPrice.access()
		self.player.debt += self.card.debtPrice.access()
		return True
		
class Buy(Event):
	name = 'Buy'
	def setup(self, **kwargs):
		if not hasattr(self, 'to'): self.to = self.player.discardPile
	def payload(self, **kwargs):
		if not self.spawnTree(Pay).resolve(): return
		return self.spawnTree(Gain).resolve()
		
class Purchase(Event):
	name = 'Purchase'
	def payload(self, **kwargs):
		if not self.spawnTree(CanPay).resolve(): return
		return self.spawnTree(Buy).resolve()
		
class BuyDEvent(Event):
	name = 'BuyDEvent'
	def payload(self, **kwargs):
		if not self.spawnTree(Pay).resolve(): return
		self.card.onBuy(self.player)
		
class PurchaseDEvent(Event):
	name = 'PurchaseDEvent'
	def payload(self, **kwargs):
		if not self.spawnTree(CanPay).resolve(): return
		return self.spawnTree(BuyDEvent).resolve()
		
class PurchaseFromPile(Event):
	name = 'PurchaseFromPile'
	def setup(self, **kwargs):
		self.card = self.frm.viewTop()
	def payload(self, **kwargs):
		if not self.card: return
		return self.spawnTree(Purchase).resolve()
		
class FlipJourney(Event):
	name = 'FlipJourney'
	def payload(self, **kwargs):
		player.journey = not player.journey
		return player.journey
		
class PayDebt(Event):
	name = 'PayDebt'
	def payload(self, **kwargs):
		if self.player.debt<1: return
		amount = self.player.user(list(range(min(self.player.debt, self.player.coins)+1)), 'Choose amount')
		if amount==0: return
		self.player.debt -= amount
		self.player.coins -= amount
		
class Reveal(Event):
	name = 'Reveal'
	def payload(self, **kwargs):
		pass
		
class Message(Event):
	name = 'Message'
	def payload(self, **kwargs):
		pass
		
class ResolveAttack(Event):
	name = 'ResolveAttack'
	def payload(self, **kwargs):
		self.attack(self.victim, **kwargs)
		
class MoveToken(Event):
	name = 'MoveToken'
	def payload(self, **kwargs):
		print('---------------------------')
		print(self.frm, self.token, self.to, self.to.tokens)
		i = self.frm.index(self.token)
		print(i)
		if i==None: return
		print('wow')
		self.token = self.frm.pop(i)
		
		self.spawn(AddToken).resolve()
		return self.token
		
class AddToken(Event):
	name = 'AddToken'
	def payload(self, **kwargs):
		print('ADDTOKEN')
		if hasattr(self.to, 'tokens'): self.to.tokens.append(self.token)
		else: self.to.append(self.tokens)
		self.token.owner = self.to
		
class MakeToken(Event):
	name = 'MakeToken'
	def payload(self, **kwargs):
		self.token.playerOwner = self.player
		self.player.tokens[self.token.name] = self.token
		
class ResolveDuration(Event):
	name = 'ResolveDuration'
	def payload(self, **kwargs):
		self.card.duration(**kwargs)
		
class DiscardDeck(Event):
	name = 'DiscardDeck'
	def payload(self, **kwargs):
		for card in copy.copy(self.player.library): self.spawnTree(MoveCard, frm=self.player.library, to=self.player.discardPile, card=card).resolve()