import java.util.Scanner;

public class Blackjack {

    public static Scanner scan = new Scanner(System.in);

    public static void main(String[] args) {
        System.out.println("\nWelcome to Java Casino!");
        System.out.println("Do you have a knack for Black Jack?");
        System.out.println("We shall see..");
        System.out.println("..Ready? Press anything to begin!");
        //Task 3 – Wait for the user to press enter.
        scan.nextLine();
        //Task 4 – Get two random cards.
        //       – Print them: \n You get a \n" + <randomCard> + "\n and a \n" + <randomCard>
        int handValue = 0;
        int random1 = drawRandomCard();
        String card1 = cardString(random1);
        int random2 = drawRandomCard();
        String card2 = cardString(random2);

        if (random1 == 10 || random1 == 11 || random1 == 12 || random1 == 13) {
            random1 = 10;
        }
        if (random2 == 10 || random2 == 11 || random2 == 12 || random2 == 13) {
            random2 = 10;
        }


        System.out.print("your cards \n" + card1 + card2 + "\n");

        //Task 5 – Print the sum of your hand value.
        //       – print: your total is: <hand value>
        handValue = random1 + random2;
        System.out.println("your total is: " + handValue);
        scan.nextLine();

        
        //Task 6 – Get two random cards for the dealer.
        //       – Print: The dealer shows \n" + <first card> + "\nand has a card facing down \n" + <facedown card>
        //       – Print: \nThe dealer's total is hidden

        int delearHand = 0;
        int random3 = drawRandomCard();
        String card3 = cardString(random3);
        if (random3 == 10 || random3 == 11 || random3 == 12 || random3 == 13) {
            random3 = 10;
        }
        int random4 = drawRandomCard();
        String card4 = cardString(random4);
        if (random4 == 10 || random4 == 11 || random4 == 12 || random4 == 13) {
            random4 = 10;
        }
        String faceDown = faceDown();

        delearHand = random3 + random4;

        System.out.println("The dealer shows \n" + card3 + faceDown);
        System.out.println("\nThe dealer's total is hidden");

       
        //Task 8 – Keep asking the player to hit or stay (while loop).
        //       1. Every time the player hits
        //             – draw a new card.
        //             – calculate their new total.
        //             – print: (new line) You get a (new line) <show new card>.
        //             - print: your new total is <total>

        //       2. Once the player stays, break the loop. 
        System.out.println("type: hit or stay");
        String decision = scan.nextLine();
        if (handValue == 21) {
            System.out.println("you won!");
        }
        if (decision.equals("hit")) {
            //while (decision.equals("hit")) {
            int random5 = drawRandomCard();
            String card5 = cardString(random5);
            if (random5 == 10 || random5 == 11 || random5 == 12 || random5 == 13) {
                random5 = 10;
            }
            System.out.println(card5);
            System.out.println("");
            handValue += random5;
            System.out.println("total: " + handValue);
            if (handValue > 21) {
                System.out.println("busted!");
            }
            else {
                System.out.println("type: hit or stay");
                decision = scan.nextLine();
            }
            
        }
        if (decision.equals("stay")) {
            while (true) {
                break;
            }
        }

        System.out.println("* delear's hand flops *");
        System.out.println("The dealer shows \n" + card3 + card4);
        System.out.println("delears total: " + delearHand);

        while (delearHand < 17) {
            int random6 = drawRandomCard();
            String card6 = cardString(random6);
            if (random6 == 10 || random6 == 11 || random6 == 12 || random6 == 13) {
                random6 = 10;
            }
            System.out.println(card6);
            System.out.println("");
            delearHand += random6;
            System.out.println("delears total: " + delearHand);
        }
        if (delearHand >= 17 && delearHand <= 21) {
            if (delearHand == handValue) {
                System.out.println("we tied");
            }
            if (delearHand > handValue) {
                System.out.println("You lost!");
            }
            if (delearHand < handValue) {
                System.out.println("You won!");
            }
        }
        if (delearHand > 21) {
            System.out.println("delear busted");
            System.out.println("you won!");
        }
        
        //For tasks 9 to 13, see the article: Blackjack Part II. 
         scan.close();

    }

    /** Task 1 – make a function that returns a random number between 1 and 13
     * Function name – drawRandomCard
     * @return (int)
     *
     * Inside the function:
     *   1. Gets a random number between 1 and 13.
     *   2. Returns a card.
     */
    public static int drawRandomCard() {
        int randomCard = (int) (Math.random() * 13 + 1);
        return randomCard;
    }

    /** Task 2 – make a function that returns a String drawing of the card.
     * Function name – cardString
     * @param cardNumber (int)
     * @return (String)
     *
     * Inside the function:
     *   1. Returns a String drawing of the card.
     */
    public static String cardString (int randomCard) {
        if (randomCard == 1) {
            return "   _____\n" +
                    "  |A _  |\n" +
                    "  | ( ) |\n" +
                    "  |(_'_)|\n" +
                    "  |  |  |\n" +
                    "  |____V|\n";
        }
        if (randomCard == 2) {
            return "   _____\n" +
                    "  |2    |\n" +
                    "  |  o  |\n" +
                    "  |     |\n" +
                    "  |  o  |\n" +
                    "  |____Z|\n";
        }
        if (randomCard == 3) {
            return "   _____\n" +
                    "  |3    |\n" +
                    "  | o o |\n" +
                    "  |     |\n" +
                    "  |  o  |\n" +
                    "  |____E|\n";
        }
        if (randomCard == 4) {
            return "   _____\n" +
                    "  |4    |\n" +
                    "  | o o |\n" +
                    "  |     |\n" +
                    "  | o o |\n" +
                    "  |____h|\n";
        }
        if (randomCard == 5) {
            return "   _____ \n" +
                    "  |5    |\n" +
                    "  | o o |\n" +
                    "  |  o  |\n" +
                    "  | o o |\n" +
                    "  |____S|\n";
        }
        if (randomCard == 6) {
            return "   _____ \n" +
                    "  |6    |\n" +
                    "  | o o |\n" +
                    "  | o o |\n" +
                    "  | o o |\n" +
                    "  |____6|\n";
        }
        if (randomCard == 7) {
            return "   _____ \n" +
                    "  |7    |\n" +
                    "  | o o |\n" +
                    "  |o o o|\n" +
                    "  | o o |\n" +
                    "  |____7|\n";
        }
        if (randomCard == 8) {
            return "   _____ \n" +
                    "  |8    |\n" +
                    "  |o o o|\n" +
                    "  | o o |\n" +
                    "  |o o o|\n" +
                    "  |____8|\n";
        }
        if (randomCard == 9) {
            return "   _____ \n" +
                    "  |9    |\n" +
                    "  |o o o|\n" +
                    "  |o o o|\n" +
                    "  |o o o|\n" +
                    "  |____9|\n";
        }
        if (randomCard == 10) {
            return "   _____ \n" +
                    "  |10  o|\n" +
                    "  |o o o|\n" +
                    "  |o o o|\n" +
                    "  |o o o|\n" +
                    "  |___10|\n";
        }
        if (randomCard == 11) {
            return "   _____\n" +
                    "  |J  ww|\n" +
                    "  | o {)|\n" +
                    "  |o o% |\n" +
                    "  | | % |\n" +
                    "  |__%%[|\n";
        }
        if (randomCard == 12) {
            return "   _____\n" +
                    "  |Q  ww|\n" +
                    "  | o {(|\n" +
                    "  |o o%%|\n" +
                    "  | |%%%|\n" +
                    "  |_%%%O|\n";
        }
        if (randomCard == 13) {
            return "   _____\n" +
                    "  |K  WW|\n" +
                    "  | o {)|\n" +
                    "  |o o%%|\n" +
                    "  | |%%%|\n" +
                    "  |_%%%>|\n";
        }

        else {
            return "card aint available";
        }
    }


    public static String faceDown() {
        return
        "   _____\n"+
        "  |     |\n"+ 
        "  |  J  |\n"+
        "  | JJJ |\n"+
        "  |  J  |\n"+
        "  |_____|\n";
    }
    
    /** Task 7 – make a function that asks the user to hit or stay.
     * Function name – hitOrStay
     * @return (String)
     *
     * Inside the function:
     *   1. Asks the user to hit or stay.
     *   2. If the user doesn't enter "hit" or "stay", keep asking them to try again by printing:
     *      Please write 'hit' or 'stay'
     *   3. Returns the user's option 
     */
    }

