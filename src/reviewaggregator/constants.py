WELCOME_EMAIL_SUBJECT = "Welcome to Review Aggregator!"
WELCOME_EMAIL_MESSAGE = lambda username: f"""Hi {username},\n\nThanks for signing up for Review Aggregator. 
                                    \n\nYou can now start tracking and aggregating reviews for your SaaS products.
                                    \n\nGet started by logging in and exploring your dashboard.\n\n— The Review Aggregator Team"""
                                    
PLAN_EMAIL_SUBJECT = "Your Review Aggregator Plan was Updated"
PLAN_EMAIL_MESSAGE = lambda username, plan_name: f"""Hi {username},\n\nYour Review Aggregator plan was updated to {plan_name}. 
                                    \n\nYou can now enjoy the benefits of your new plan and continue tracking and aggregating reviews for your SaaS products.
                                    \n\nIf you have any questions or need assistance, feel free to reach out to our support team.
                                    \n\n— The Review Aggregator Team"""