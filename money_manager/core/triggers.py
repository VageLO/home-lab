update_balance_on_transaction_delete = '''
CREATE TRIGGER Update_Balance_On_Transaction_Delete
AFTER DELETE ON Transactions
FOR EACH ROW

BEGIN
	UPDATE Accounts
	SET balance = CASE
		WHEN old.transaction_type = 'Withdrawal' OR old.transaction_type = 'Transfer'
		THEN ROUND((SELECT balance FROM Accounts WHERE id = old.account_id) + old.amount, 2)
		
		WHEN old.transaction_type = 'Deposit'
		THEN ROUND((SELECT balance FROM Accounts WHERE id = old.account_id) - old.amount, 2)
		
		ELSE RAISE(ABORT, "ELSE UPDATE Accounts ON DELETE")
	END WHERE id = old.account_id;
	
	UPDATE Accounts
	SET balance = CASE
		WHEN old.to_account_id IS NOT NULL AND (old.to_amount IS NOT NULL AND old.to_amount <> 0)
		THEN ROUND((SELECT balance FROM Accounts WHERE id = old.to_account_id) - old.to_amount, 2)
		
		WHEN old.to_account_id IS NOT NULL AND old.amount IS NOT NULL
		THEN ROUND((SELECT balance FROM Accounts WHERE id = old.to_account_id) - old.amount, 2)
		
		ELSE RAISE(IGNORE)
	END WHERE id = old.to_account_id;
END
'''

update_balance_on_transaction_insert = '''
CREATE TRIGGER Update_Balance_On_Transaction_Insert
AFTER INSERT ON Transactions
FOR EACH ROW

BEGIN
	UPDATE Accounts
	SET balance = CASE
		WHEN new.transaction_type = 'Withdrawal' OR new.transaction_type = 'Transfer'
		THEN ROUND((SELECT balance FROM Accounts WHERE id = new.account_id) - new.amount, 2)
		
		WHEN new.transaction_type = 'Deposit'
		THEN ROUND((SELECT balance FROM Accounts WHERE id = new.account_id) + new.amount, 2)
		
		ELSE RAISE(IGNORE)
	END WHERE id = new.account_id;
	
	UPDATE Accounts
	SET balance = CASE
		WHEN new.to_account_id IS NOT NULL AND (new.to_amount IS NOT NULL AND new.to_amount <> 0)
		THEN ROUND((SELECT balance FROM Accounts WHERE id = new.to_account_id) + new.to_amount, 2)
		
		WHEN new.to_account_id IS NOT NULL AND new.amount IS NOT NULL
		THEN ROUND((SELECT balance FROM Accounts WHERE id = new.to_account_id) + new.amount, 2)
		
		ELSE RAISE(IGNORE)
	END WHERE id = new.to_account_id;
END;
'''

update_balance_on_transaction_update = '''
CREATE TRIGGER Update_Balance_On_Transaction_Update
AFTER UPDATE ON Transactions
FOR EACH ROW

BEGIN

	UPDATE Accounts
	SET balance = CASE
		-- Update new.account if new.account_id EQUAL old.account_id
		WHEN new.account_id = old.account_id
		THEN CASE
			WHEN new.transaction_type = 'Withdrawal' AND (old.transaction_type = 'Withdrawal' OR old.transaction_type = 'Transfer')
			THEN ROUND(((SELECT balance FROM Accounts WHERE id = new.account_id) + old.amount) - new.amount, 2)
			
			WHEN new.transaction_type = 'Withdrawal' AND old.transaction_type = 'Deposit'
			THEN ROUND(((SELECT balance FROM Accounts WHERE id = new.account_id) - old.amount) - new.amount, 2)
			
			WHEN new.transaction_type = 'Deposit' AND (old.transaction_type = 'Withdrawal' OR old.transaction_type = 'Transfer')
			THEN ROUND(((SELECT balance FROM Accounts WHERE id = new.account_id) + old.amount) + new.amount, 2)
			
			WHEN new.transaction_type = 'Deposit' AND old.transaction_type = 'Deposit'
			THEN ROUND(((SELECT balance FROM Accounts WHERE id = new.account_id) - old.amount) + new.amount, 2)
			
			WHEN new.transaction_type = 'Transfer' AND (old.transaction_type = 'Withdrawal' OR old.transaction_type = 'Transfer')
			THEN ROUND(((SELECT balance FROM Accounts WHERE id = new.account_id) + old.amount) - new.amount, 2)
			
			WHEN new.transaction_type = 'Transfer' AND old.transaction_type = 'Deposit'
			THEN ROUND(((SELECT balance FROM Accounts WHERE id = new.account_id) - old.amount) - new.amount, 2)

			ELSE RAISE(ABORT, "-- Update new.account if new.account_id EQUAL old.account_id")
			END
			
		WHEN new.account_id <> old.account_id
		THEN CASE
			WHEN new.transaction_type = 'Withdrawal' OR new.transaction_type = 'Transfer'
			THEN ROUND((SELECT balance FROM Accounts WHERE id = new.account_id) - new.amount, 2)

			WHEN new.transaction_type = 'Deposit'
			THEN ROUND((SELECT balance FROM Accounts WHERE id = new.account_id) + new.amount, 2)

			ELSE RAISE(ABORT, "-- Update new.account if new.account_id NOT EQUAL old.account_id")
			END

	END WHERE id = new.account_id;
	
	-- Update old.account if new.account_id NOT EQUAL old.account_id
	UPDATE Accounts
	SET balance = CASE
		WHEN new.account_id <> old.account_id
		THEN CASE 
			WHEN old.transaction_type = 'Withdrawal' OR old.transaction_type = 'Transfer'
			THEN ROUND((SELECT balance FROM Accounts WHERE id = old.account_id) + old.amount, 2)

			WHEN old.transaction_type = 'Deposit'
			THEN ROUND((SELECT balance FROM Accounts WHERE id = old.account_id) - old.amount, 2)

			ELSE RAISE(ABORT, "Update old.account if new.account_id NOT EQUAL old.account_id")
			END
		ELSE RAISE(IGNORE)
	END WHERE id = old.account_id;
	
END;
'''

update_to_account_balance = '''
CREATE TRIGGER Update_ToAccount_Balance
AFTER UPDATE ON Transactions
FOR EACH ROW

BEGIN
	
	-- Update new.to_account with NEW data
	UPDATE Accounts
	SET balance = CASE
		WHEN new.to_account_id IS NOT NULL AND (new.to_amount IS NOT NULL AND new.to_amount <> 0)
		THEN ROUND((SELECT balance FROM Accounts WHERE id = new.to_account_id) + new.to_amount, 2)
		
		WHEN new.to_account_id IS NOT NULL AND new.amount IS NOT NULL
		THEN ROUND((SELECT balance FROM Accounts WHERE id = new.to_account_id) + new.amount, 2)
		
		ELSE RAISE(ABORT, "Update new.to_account with NEW data")
	END WHERE id = new.to_account_id;
	
	-- Update old.to_account with OLD data
	UPDATE Accounts
	SET balance = CASE
		WHEN old.to_account_id IS NOT NULL AND (old.to_amount IS NOT NULL AND old.to_amount <> 0)
		THEN ROUND((SELECT balance FROM Accounts WHERE id = old.to_account_id) - old.to_amount, 2)
		
		WHEN old.to_account_id IS NOT NULL AND old.amount IS NOT NULL
		THEN ROUND((SELECT balance FROM Accounts WHERE id = old.to_account_id) - old.amount, 2)
		
		ELSE RAISE(ABORT, "Update old.to_account with OLD data")
	END WHERE id = old.to_account_id;
	
END
'''
