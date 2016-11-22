from FullEvent import *
import random
import numpy as np

class TriggerThisTurn(Continuous, Trigger):
	name = 'BaseThisTurn'
	defaultTerminatorTrigger = 'turnEnded'

class ReplaceThisTurn(Continuous, Replacement):
	name = 'BaseReplaceThisTurn'
	defaultTerminatorTrigger = 'turnEnded'
	
class MoveCard(Event):
	name = 'MoveCard'
	def check(self, **kwargs):
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
		if self.card.owner: self.card.owner.owns.remove(self.card)
		self.card.setOwner(None)
		
class Gain(Event):
	name = 'Gain'
	def setup(self, **kwargs):
		if not hasattr(self, 'to'): self.to = self.player.discardPile
	def check(self, **kwargs):
		self.gainedCard = self.spawnTree(MoveCard).resolve()
		if not self.gainedCard: return True
	def payload(self, **kwargs):
		self.spawn(GainOwnership).resolve()
		return self.gainedCard
		
class GainFromPile(Event):
	name = 'GainFromPile'
	def check(self, **kwargs):
		self.card = self.frm.viewTop()
		if not self.card: return True
	def payload(self, **kwargs):
		return self.spawnTree(Gain).resolve()
		
class Take(Event):
	name = 'Take'
	def setup(self, **kwargs):
		if not hasattr(self, 'to'): self.to = self.player.discardPile
	def check(self, **kwargs):
		self.gainedCard = self.spawnTree(MoveCard).resolve()
		if not self.gainedCard: return True
	def payload(self, **kwargs):
		self.spawn(GainOwnership).resolve()
		return self.gainedCard
		
class TakeFromPile(Event):
	name = 'TakeFromPile'
	def check(self, **kwargs):
		self.card = self.frm.viewTop()
		if not self.card: return True
	def payload(self, **kwargs):
		return self.spawnTree(Take).resolve()
		
class Discard(Event):
	name = 'Discard'
	def setup(self, **kwargs):
		if not hasattr(self, 'frm'): self.frm = self.player.hand
		if not hasattr(self, 'to'): self.to = self.player.discardPile
	def check(self, **kwargs):
		self.discardedCard = self.spawnTree(MoveCard).resolve()
		if not self.discardedCard: return True
	def payload(self, **kwargs):
		return self.discardedCard
		
class Destroy(Event):
	name = 'Destroy'
	def setup(self, **kwargs):
		if not hasattr(self, 'frm'): self.frm = self.player.inPlay
		if not hasattr(self, 'to'): self.to = self.player.discardPile
	def check(self, **kwargs):
		self.destroyedCard = self.spawnTree(MoveCard).resolve()
		if not self.destroyedCard: return True
	def payload(self, **kwargs):
		return self.destroyedCard
		
class Trash(Event):
	name = 'Trash'
	def setup(self, **kwargs):
		self.to = self.session.trash
	def check(self, **kwargs):
		self.trashedCard = self.spawnTree(MoveCard).resolve()
		if not self.trashedCard: return True
	def payload(self, **kwargs):
		self.spawn(LooseOwnership).resolve()
		return self.trashedCard
		
class PutBackCard(Event):
	name = 'PutBackCard'
	def setup(self, **kwargs):
		if not hasattr(self, 'to') and self.card.frmPile:
			self.to = self.card.frmPile
	def check(self, **kwargs):
		if not hasattr(self, 'to'): return True
		self.returnedCard = self.spawnTree(MoveCard).resolve()
		if not self.returnedCard: return True
	def payload(self, **kwargs):
		self.spawn(LooseOwnership).resolve()
		return self.returnedCard
		
class ReturnCard(Event):
	name = 'ReturnCard'
	def setup(self, **kwargs):
		if not hasattr(self, 'to') and self.card.frmPile and self.card.frmPile.name in self.session.piles:
			self.to = self.card.frmPile
	def check(self, **kwargs):
		if not hasattr(self, 'to'): return True
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
	def check(self, **kwargs):
		card = self.spawnTree(MoveCard).resolve()
		if not card: return True
	def payload(self, **kwargs):
		self.spawnTree(PlayCard).resolve()
		return True
		
class AddCoin(Event):
	name = 'AddCoin'
	def setup(self, **kwargs):
		if not hasattr(self, 'amnt'): self.amnt = 1
	def check(self, **kwargs):
		if self.amnt<1: return True
		if self.player.minusCoin:
			self.amnt -= 1
			self.player.minusCoin = False
		if self.amnt<1: return True
	def payload(self, **kwargs):
		self.player.coins += self.amnt
		
class AddPotion(Event):
	name = 'AddPotion'
	def setup(self, **kwargs):
		if not hasattr(self, 'amnt'): self.amnt = 1
		if self.amnt==0: return True
	def payload(self, **kwargs):
		self.player.potions += self.amnt
		
class AddDebt(Event):
	name = 'AddDebt'
	def setup(self, **kwargs):
		if not hasattr(self, 'amnt'): self.amnt = 1
		if self.amnt==0: return True
	def payload(self, **kwargs):
		self.player.debt += self.amnt

class AddAction(Event):
	name = 'AddAction'
	def setup(self, **kwargs):
		if not hasattr(self, 'amnt'): self.amnt = 1
		if self.amnt==0: return True
	def payload(self, **kwargs):
		self.player.actions += self.amnt

class AddBuy(Event):
	name = 'AddBuy'
	def setup(self, **kwargs):
		if not hasattr(self, 'amnt'): self.amnt = 1
		if self.amnt==0: return True
	def payload(self, **kwargs):
		self.player.buys += self.amnt
		
class AddVictory(Event):
	name = 'AddVictory'
	def setup(self, **kwargs):
		if not hasattr(self, 'amnt'): self.amnt = 1
		if self.amnt==0: return True
	def payload(self, **kwargs):
		self.player.victories += self.amnt
		
class Shuffle(Event):
	name = 'Shuffle'
	def payload(self, **kwargs):
		random.shuffle(self.player.library)
		
class Reshuffle(Event):
	name = 'Reshuffle'
	def payload(self, **kwargs):
		while self.player.discardPile: self.player.library.append(self.player.discardPile.pop())
		self.spawnTree(Shuffle).resolve()
		
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
	def check(self, **kwargs):
		if self.player.minusDraw:
			self.player.minusDraw = False
			return True
		self.card = self.spawnTree(RequestCard).resolve()
		if not self.card: return True
	def payload(self, **kwargs):
		return self.spawnTree(MoveCard).resolve()
			
class DrawCards(Event):
	name = 'DrawCards'
	def setup(self, **kwargs):
		if not hasattr(self, 'amnt'): self.amnt = 1
	def check(self, **kwargs):
		if self.amnt<1: return True
		if self.player.minusDraw:
			self.player.minusDraw = False
			self.amnt -= 1
		if self.amnt<1: return True
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
	def check(self, **kwargs):
		if not self.card: return True
	def payload(self, **kwargs):
		return self.spawnTree(Purchase).resolve()
		
class FlipJourney(Event):
	name = 'FlipJourney'
	def payload(self, **kwargs):
		self.player.journey = not self.player.journey
		return self.player.journey
		
class PayDebt(Event):
	name = 'PayDebt'
	def check(self, **kwargs):
		if self.player.debt<1: return True
	def payload(self, **kwargs):
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
		d = copy.copy(self.__dict__)
		d.pop('player', None)
		return self.attack(self.victim, **d)
		
class MoveToken(Event):
	name = 'MoveToken'
	def payload(self, **kwargs):
		i = self.frm.tokens.index(self.token)
		if i==None: return
		self.token = self.frm.tokens.pop(i)
		self.spawn(AddToken).resolve()
		return self.token
		
class AddToken(Event):
	name = 'AddToken'
	def payload(self, **kwargs):
		if hasattr(self.to, 'tokens'): self.to.tokens.append(self.token)
		else: self.to.append(self.token)
		self.token.owner = self.to
		
class MakeToken(Event):
	name = 'MakeToken'
	def payload(self, **kwargs):
		self.token.playerOwner = self.player
		self.player.tokens[self.token.name] = self.token
		
class DestroyToken(Event):
	name = 'DestroyToken'
	def check(self, **kwargs):
		if not self.token in self.frm.tokens: return True
	def payload(self, **kwargs):
		self.frm.tokens.remove(self.token)
		return self.token
		
class TakeVPs(Event):
	name = 'TakeVPs'
	def setup(self, **kwargs):
		if not hasattr(self, 'amnt'): self.amnt = None
	def payload(self, **kwargs):
		self.taken = 0
		for token in copy.copy(self.frm.tokens):
			if token.name=='VP Token' and self.spawnTree(DestroyToken, token=token).resolve(): self.taken+=1
			if self.amnt!=None and self.taken>=self.amnt: break
		self.amnt = self.taken
		self.spawnTree(AddVictory).resolve()
				
class ResolveDuration(Event):
	name = 'ResolveDuration'
	def payload(self, **kwargs):
		self.card.duration(self.player, **kwargs)
		
class DiscardDeck(Event):
	name = 'DiscardDeck'
	def payload(self, **kwargs):
		for card in copy.copy(self.player.library): self.spawnTree(MoveCard, frm=self.player.library, to=self.player.discardPile, card=card).resolve()
		
class DoubleMoney(Event):
	name = 'DoubleMoney'
	def payload(self, **kwargs):
		self.spawnTree(AddCoin, amnt=self.player.coins)
		
class TakeMinusDraw(Event):
	name = 'TakeMinusDraw'
	def check(self, **kwargs):
		if self.player.minusDraw: return True
	def payload(self, **kwargs):
		self.player.minusDraw = True
		
class TakeMinusCoin(Event):
	name = 'TakeMinusCoin'
	def check(self, **kwargs):
		if self.player.minusCoin: return True
	def payload(self, **kwargs):
		self.player.minusCoin = True