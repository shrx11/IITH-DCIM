import java.io.IOException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.chrome.ChromeDriver;
import org.testng.annotations.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.support.ui.Select;

public class AddPermission {

        public static void main(String[] args) throws IOException, InterruptedException {
                System.setProperty("webdriver.chrome.driver", "/usr/bin/chromedriver");
                ChromeOptions chromeOptions = new ChromeOptions();
                // chromeOptions.addArguments("--headless");
                chromeOptions.addArguments("--no-sandbox");
                chromeOptions.addArguments("--ignore-ssl-errors=yes");
                chromeOptions.addArguments("--ignore-certificate-errors");
                WebDriver driver = new ChromeDriver(chromeOptions);

                driver.get("http://192.168.50.76/login/?next=/");
                Thread.sleep(1000);

                driver.findElement(By.xpath("//input[@name='username']")).sendKeys("admin");
                driver.findElement(By.xpath("//input[@name='password']")).sendKeys("admin@123");
                driver.findElement(By.xpath("//button[@type='submit']")).submit();
                Thread.sleep(2000);

                driver.get("http://192.168.50.76/admin/users/objectpermission/add/");
                
                String name = args[0];
                String word = name;
                boolean admin = false;
                if(name.endsWith("admin"))
                        admin = true;                

                System.out.println(name);
                
                driver.findElement(By.xpath("//input[@name='name']")).sendKeys(args[0]);
                
                driver.findElements(By.xpath("//input[@type='checkbox']")).get(1).click();
                if(admin)
                {
                        driver.findElements(By.xpath("//input[@type='checkbox']")).get(2).click();     
                        driver.findElements(By.xpath("//input[@type='checkbox']")).get(3).click();
                        driver.findElements(By.xpath("//input[@type='checkbox']")).get(4).click();
                }

                driver.findElement(By.xpath("//option[text()='DCIM > Device']")).click();

                driver.findElement(By.xpath("//option[text()='" + name + "']")).click();

                driver.findElements(By.xpath("//a[@title='Choose']")).get(0).click();
                
                if(name.contains("admin") || name.contains("users"))
                        word = name.substring(0, name.length()-6);

                driver.findElement(By.xpath("//textarea")).clear();
                Thread.sleep(1000);
                driver.findElement(By.xpath("//textarea")).sendKeys("[{\"site__slug\": \"" + word.toLowerCase() + "\"}]");
                driver.findElements(By.xpath("//input[@type='submit']")).get(1).click();

                Thread.sleep(2000);
                System.out.println("Successfully Added Device Permission");

                driver.findElement(By.xpath("//input[@name='name']")).sendKeys(args[0]);
                
                driver.findElements(By.xpath("//input[@type='checkbox']")).get(1).click();
                if(admin)
                {
                        driver.findElements(By.xpath("//input[@type='checkbox']")).get(2).click();     
                        driver.findElements(By.xpath("//input[@type='checkbox']")).get(3).click();
                        driver.findElements(By.xpath("//input[@type='checkbox']")).get(4).click();
                }

                driver.findElement(By.xpath("//option[text()='DCIM > Site']")).click();

                driver.findElement(By.xpath("//option[text()='" + name + "']")).click();

                driver.findElements(By.xpath("//a[@title='Choose']")).get(0).click();
                
                if(name.contains("admin") || name.contains("users"))
                        word = name.substring(0, name.length()-6);

                driver.findElement(By.xpath("//textarea")).clear();
                Thread.sleep(1000);
                driver.findElement(By.xpath("//textarea")).sendKeys("[{\"slug\": \"" + word.toLowerCase() + "\"}]");
                driver.findElements(By.xpath("//input[@type='submit']")).get(0).click();

                Thread.sleep(2000);

                System.out.println("Successfully Added Site Permission");
                driver.quit();
        }
}
