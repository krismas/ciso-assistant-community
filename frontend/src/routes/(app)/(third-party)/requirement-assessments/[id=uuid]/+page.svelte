<script lang="ts">
	import { page } from '$app/stores';
	import ModelTable from '$lib/components/ModelTable/ModelTable.svelte';
	import { complianceResultColorMap, complianceStatusColorMap } from '$lib/utils/constants';
	import {
		displayScoreColor,
		formatScoreValue,
		getRequirementTitle,
		getSecureRedirect
	} from '$lib/utils/helpers';
	import { safeTranslate } from '$lib/utils/i18n';
	import { toCamelCase } from '$lib/utils/locales';
	import { hideSuggestions } from '$lib/utils/stores';
	import { m } from '$paraglide/messages';
	import { ProgressRadial, Tab, TabGroup } from '@skeletonlabs/skeleton';
	import type { PageData } from '../[id=uuid]/$types';

	export let data: PageData;
	const threats = data.requirementAssessment.requirement.associated_threats ?? [];
	const reference_controls =
		data.requirementAssessment.requirement.associated_reference_controls ?? [];
	const annotation = data.requirement.annotation;
	const typical_evidence = data.requirement.typical_evidence;

	const has_threats = threats.length > 0;
	const has_reference_controls = reference_controls.length > 0;

	$: mappingInference = {
		sourceRequirementAssessment:
			data.requirementAssessment.mapping_inference.source_requirement_assessment,
		result: data.requirementAssessment.mapping_inference.result,
		annotation: ''
	};

	const title = getRequirementTitle(data.requirement.ref_id, data.requirement.name)
		? getRequirementTitle(data.requirement.ref_id, data.requirement.name)
		: getRequirementTitle(data.parent.ref_id, data.parent.name);

	let requirementAssessmentsList: string[] = $hideSuggestions;

	let hideSuggestion = requirementAssessmentsList.includes(data.requirementAssessment.id)
		? true
		: false;

	function toggleSuggestions() {
		if (!requirementAssessmentsList.includes(data.requirementAssessment.id)) {
			requirementAssessmentsList.push(data.requirementAssessment.id);
		} else {
			requirementAssessmentsList = requirementAssessmentsList.filter(
				(item) => item !== data.requirementAssessment.id
			);
		}
		hideSuggestion = !hideSuggestion;
		hideSuggestions.set(requirementAssessmentsList);
	}

	function cancel(): void {
		var currentUrl = window.location.href;
		var url = new URL(currentUrl);
		var nextValue = getSecureRedirect(url.searchParams.get('next'));
		if (nextValue) window.location.href = nextValue;
	}

	$: classesText =
		complianceResultColorMap[mappingInference.result] === '#000000' ? 'text-white' : '';

	const max_score = data.complianceAssessmentScore.max_score;
	const score = data.requirementAssessment.score;
	const documentationScore = data.requirementAssessment.documentation_score;

	let tabSet = $page.data.user.is_third_party ? 1 : 0;
</script>

<div class="card space-y-2 p-4 bg-white shadow">
	<div class="flex flex-row space-x-2 items-center">
		<code class="code">{data.requirement.urn}</code>
		<span
			class="badge h-fit"
			style="background-color: {complianceStatusColorMap[data.requirementAssessment.status] ??
				'#d1d5db'};"
		>
			{safeTranslate(data.requirementAssessment.status)}
		</span>
		<span
			class="badge {classesText} h-fit"
			style="background-color: {complianceResultColorMap[data.requirementAssessment.result] ??
				'#d1d5db'};"
		>
			{safeTranslate(data.requirementAssessment.result)}
		</span>
		{#if data.requirementAssessment.is_scored}
			<ProgressRadial
				stroke={100}
				meter={displayScoreColor(score, max_score)}
				value={formatScoreValue(score, max_score)}
				font={150}
				class="shrink-0"
				width={'w-10'}>{score}</ProgressRadial
			>
			{#if data.complianceAssessmentScore.show_documentation_score}
				<ProgressRadial
					stroke={100}
					meter={displayScoreColor(documentationScore, max_score)}
					value={formatScoreValue(documentationScore, max_score)}
					font={150}
					class="shrink-0"
					width={'w-10'}>{documentationScore}</ProgressRadial
				>
			{/if}
		{/if}
	</div>
	{#if data.requirement.description}
		<p class="whitespace-pre-line p-2 font-light text-lg">
			👉 {data.requirement.description}
		</p>
	{/if}
	{#if has_threats || has_reference_controls || annotation || mappingInference.result}
		<div class="card p-4 variant-glass-primary text-sm flex flex-col justify-evenly cursor-auto">
			<h2 class="font-semibold text-lg flex flex-row justify-between">
				<div>
					<i class="fa-solid fa-circle-info mr-2" />{m.additionalInformation()}
				</div>
				<button on:click={toggleSuggestions}>
					{#if !hideSuggestion}
						<i class="fa-solid fa-eye" />
					{:else}
						<i class="fa-solid fa-eye-slash" />
					{/if}
				</button>
			</h2>
			{#if !hideSuggestion}
				{#if has_threats || has_reference_controls}
					<div class="my-2 flex flex-col">
						<div class="flex-1">
							{#if reference_controls.length > 0}
								<p class="font-medium">
									<i class="fa-solid fa-gears" />
									{m.suggestedReferenceControls()}
								</p>
								<ul class="list-disc ml-4">
									{#each reference_controls as func}
										<li>
											{#if func.id}
												<a class="anchor" href="/reference-controls/{func.id}">
													{func.str}
												</a>
											{:else}
												<p>{func.str}</p>
											{/if}
										</li>
									{/each}
								</ul>
							{/if}
						</div>
						<div class="flex-1">
							{#if threats.length > 0}
								<p class="font-medium">
									<i class="fa-solid fa-gears" />
									{m.threatsCovered()}
								</p>
								<ul class="list-disc ml-4">
									{#each threats as threat}
										<li>
											{#if threat.id}
												<a class="anchor" href="/threats/{threat.id}">
													{threat.str}
												</a>
											{:else}
												<p>{threat.str}</p>
											{/if}
										</li>
									{/each}
								</ul>
							{/if}
						</div>
					</div>
				{/if}
				{#if annotation}
					<div class="my-2">
						<p class="font-medium">
							<i class="fa-solid fa-pencil" />
							{m.annotation()}
						</p>
						<p class="whitespace-pre-line py-1">
							{annotation}
						</p>
					</div>
				{/if}
				{#if typical_evidence}
					<div class="my-2">
						<p class="font-medium">
							<i class="fa-solid fa-pencil" />
							{m.typicalEvidence()}
						</p>
						<p class="whitespace-pre-line py-1">
							{typical_evidence}
						</p>
					</div>
				{/if}
				{#if mappingInference.result}
					<div class="my-2">
						<p class="font-medium">
							<i class="fa-solid fa-link" />
							{m.mappingInference()}
						</p>
						<span class="text-xs text-gray-500"
							><i class="fa-solid fa-circle-info"></i> {m.mappingInferenceHelpText()}</span
						>
						<ul class="list-disc ml-4">
							<li>
								<p>
									<a
										class="anchor"
										href="/requirement-assessments/{mappingInference.sourceRequirementAssessment
											.id}"
									>
										{mappingInference.sourceRequirementAssessment.str}
									</a>
								</p>
								<p class="whitespace-pre-line py-1">
									<span class="italic">{m.coverageColon()}</span>
									<span class="badge h-fit">
										{safeTranslate(
											toCamelCase(mappingInference.sourceRequirementAssessment.coverage)
										)}
									</span>
								</p>
								<p class="whitespace-pre-line py-1">
									<span class="italic">{m.suggestionColon()}</span>
									<span
										class="badge {classesText} h-fit"
										style="background-color: {complianceResultColorMap[mappingInference.result]};"
									>
										{safeTranslate(mappingInference.result)}
									</span>
								</p>
								{#if mappingInference.annotation}
									<p class="whitespace-pre-line py-1">
										<span class="italic">{m.annotationColon()}</span>
										{mappingInference.annotation}
									</p>
								{/if}
							</li>
						</ul>
					</div>
				{/if}
			{/if}
		</div>
	{/if}
	<div>
		<TabGroup>
			{#if !$page.data.user.is_third_party}
				<Tab bind:group={tabSet} name="compliance_assessments_tab" value={0}
					>{m.appliedControls()}
				</Tab>
			{/if}
			<Tab bind:group={tabSet} name="risk_assessments_tab" value={1}>{m.evidences()}</Tab>
			<svelte:fragment slot="panel">
				{#if tabSet === 0 && !$page.data.user.is_third_party}
					<div class="flex items-center mb-2 px-2 text-xs space-x-2">
						<i class="fa-solid fa-info-circle" />
						<p>{m.requirementAppliedControlHelpText()}</p>
					</div>
					<div
						class="h-full flex flex-col space-y-2 variant-outline-surface rounded-container-token p-4"
					>
						<ModelTable
							source={data.tables['applied-controls']}
							hideFilters={true}
							URLModel="applied-controls"
							baseEndpoint="/applied-controls?requirement_assessments={$page.data
								.requirementAssessment.id}"
						/>
					</div>
				{/if}
				{#if tabSet === 1}
					<div class="flex items-center mb-2 px-2 text-xs space-x-2">
						<i class="fa-solid fa-info-circle" />
						<p>{m.requirementEvidenceHelpText()}</p>
					</div>
					<div
						class="h-full flex flex-col space-y-2 variant-outline-surface rounded-container-token p-4"
					>
						<ModelTable
							source={data.tables['evidences']}
							hideFilters={true}
							URLModel="evidences"
							baseEndpoint="/evidences?requirement_assessments={$page.data.requirementAssessment
								.id}"
						/>
					</div>
				{/if}
			</svelte:fragment>
		</TabGroup>
	</div>
	{#if data.requirementAssessment.requirement.questions != null && Object.keys(data.requirementAssessment.requirement.questions).length !== 0}
		<h1 class="font-semibold text-sm">{m.question()}</h1>
		{#each Object.keys(data.requirementAssessment.requirement.questions) as key}
			<li class="flex justify-between items-center border rounded-xl p-2 disabled">
				{data.requirementAssessment.requirement.questions[key].text}
				{#if data.requirementAssessment.answers[key].value}
					<p class="text-sm font-semibold text-primary-500">
						{data.requirementAssessment.answers[key].value}
					</p>
				{:else}
					<p class="text-sm font-semibold text-primary-500">{m.undefined()}</p>
				{/if}
			</li>
		{/each}
	{/if}
	{#if data.requirementAssessment.observation}
		<div class="card p-4 space-y-2 variant-glass-primary">
			<h1 class="font-semibold text-sm">{m.observation()}</h1>
			<span class="text-sm">{data.requirementAssessment.observation}</span>
		</div>
	{/if}
	<div class="flex flex-row justify-between space-x-4">
		<button class="btn bg-gray-400 text-white font-semibold w-full" type="button" on:click={cancel}
			>{m.back()}</button
		>
	</div>
</div>
