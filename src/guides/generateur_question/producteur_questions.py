from typing import Any, cast

from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

from configuration import recupere_configuration
from guides.generateur_question.compteurs_thematique import calcule_nombre_questions
from guides.generateur_question.utils import (
    _charge_prompt_systeme,
    parse_questions_depuis_contenu,
)


class ProducteurQuestionsOpenAI:
    def __init__(
        self,
        *,
        client: Any | None = None,
        modele_generation: str | None = None,
        temperature: float = 0.0,
    ) -> None:
        configuration = recupere_configuration().albert
        self.client = (
            client
            if client is not None
            else OpenAI(base_url=configuration.url, api_key=configuration.cle_api)
        )
        self.modele_generation = (
            modele_generation if modele_generation is not None else configuration.modele
        )
        self.temperature = temperature

    def __call__(self, paragraphe: str) -> list[str]:
        n_questions = calcule_nombre_questions(paragraphe)
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": _charge_prompt_systeme()},
            {
                "role": "user",
                "content": (
                    f"Génère exactement {n_questions} questions.\n"
                    f"Paragraphe :\n{paragraphe}"
                ),
            },
        ]
        completion = self.client.chat.completions.create(
            model=self.modele_generation,
            messages=messages,
            temperature=self.temperature,
            stream=False,
            n=1,
        )
        completion = cast(ChatCompletion, completion)
        contenu = (completion.choices[0].message.content or "").strip()
        return parse_questions_depuis_contenu(contenu)
