*** Settings ***
Library    Browser

*** Variables ***
${URL}         https://www.tripadvisor.com/Attraction_Review-g293916-d447272-Reviews-Chinatown_Bangkok-Bangkok.html
${USER_AGENT}  Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36

*** Test Cases ***
Scrape JavaScript Page With Custom User-Agent
    New Browser    headless=false
    ${context}=    New Context    userAgent=${USER_AGENT}
    ${page}=       New Page    ${URL}
    Wait For Elements State    //div[@id="REVIEWS"]    visible    30s
    ${content}=    Get Text    //div[@id="REVIEWS"]
    Log    ${content}
    Close Browser

    
